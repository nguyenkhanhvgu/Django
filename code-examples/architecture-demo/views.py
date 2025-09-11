# Django Architecture Demo - Views
# This file demonstrates different types of Django views

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Post, Category, Tag, Comment

# =============================================================================
# FUNCTION-BASED VIEWS
# =============================================================================

def post_list(request):
    """
    Display a list of published posts with filtering and pagination
    Demonstrates: QuerySets, filtering, pagination, context data
    """
    # Get all published posts
    posts = Post.objects.filter(status='published').select_related('author', 'category')
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        posts = posts.filter(category_id=category_id)
    
    # Filter by tag if provided
    tag_id = request.GET.get('tag')
    if tag_id:
        posts = posts.filter(tags__id=tag_id)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories and tags for sidebar
    categories = Category.objects.annotate(post_count=Count('post')).filter(post_count__gt=0)
    tags = Tag.objects.annotate(post_count=Count('posts')).filter(post_count__gt=0)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'current_category': category_id,
        'current_tag': tag_id,
        'search_query': search_query,
        'page_title': 'Blog Posts'
    }
    
    return render(request, 'blog/post_list.html', context)

def post_detail(request, slug):
    """
    Display a single post with comments
    Demonstrates: get_object_or_404, related objects, view counting
    """
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Increment view count
    post.increment_view_count()
    
    # Get approved comments for this post
    comments = post.comments.filter(is_approved=True, parent=None).select_related('author')
    
    # Get related posts (same category, excluding current post)
    related_posts = Post.objects.filter(
        category=post.category, 
        status='published'
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'page_title': post.title
    }
    
    return render(request, 'blog/post_detail.html', context)

def category_detail(request, pk):
    """
    Display posts from a specific category
    Demonstrates: category filtering, object retrieval
    """
    category = get_object_or_404(Category, pk=pk)
    posts = Post.objects.filter(category=category, status='published')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'page_title': f'Posts in {category.name}'
    }
    
    return render(request, 'blog/category_detail.html', context)

@login_required
def add_comment(request, post_slug):
    """
    Add a comment to a post
    Demonstrates: POST request handling, form processing, redirects
    """
    post = get_object_or_404(Post, slug=post_slug, status='published')
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if content:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )
            messages.success(request, 'Your comment has been submitted for approval.')
        else:
            messages.error(request, 'Comment content cannot be empty.')
    
    return redirect('post_detail', slug=post_slug)

def search_posts(request):
    """
    Search posts by title and content
    Demonstrates: search functionality, Q objects
    """
    query = request.GET.get('q', '').strip()
    posts = []
    
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            status='published'
        ).select_related('author', 'category')
    
    context = {
        'posts': posts,
        'query': query,
        'page_title': f'Search Results for "{query}"' if query else 'Search'
    }
    
    return render(request, 'blog/search_results.html', context)

def api_post_list(request):
    """
    API endpoint returning posts as JSON
    Demonstrates: JSON responses, API views
    """
    posts = Post.objects.filter(status='published').values(
        'id', 'title', 'slug', 'excerpt', 'created_at', 'author__username'
    )
    
    return JsonResponse({
        'posts': list(posts),
        'count': posts.count()
    })

# =============================================================================
# CLASS-BASED VIEWS
# =============================================================================

class PostListView(ListView):
    """
    Class-based view for post listing
    Demonstrates: ListView, queryset customization, context data
    """
    model = Post
    template_name = 'blog/post_list_cbv.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Override queryset to only show published posts"""
        return Post.objects.filter(status='published').select_related('author', 'category')
    
    def get_context_data(self, **kwargs):
        """Add extra context data"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['featured_posts'] = Post.objects.filter(featured=True, status='published')[:3]
        return context

class PostDetailView(DetailView):
    """
    Class-based view for post detail
    Demonstrates: DetailView, slug-based lookup
    """
    model = Post
    template_name = 'blog/post_detail_cbv.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Only show published posts"""
        return Post.objects.filter(status='published')
    
    def get_object(self, queryset=None):
        """Override to increment view count"""
        obj = super().get_object(queryset)
        obj.increment_view_count()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(
            is_approved=True, 
            parent=None
        ).select_related('author')
        return context

class CategoryListView(ListView):
    """
    List all categories with post counts
    Demonstrates: annotations, custom queryset
    """
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.annotate(
            post_count=Count('post', filter=Q(post__status='published'))
        ).filter(post_count__gt=0)

class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new post (requires login)
    Demonstrates: CreateView, login requirement, form handling
    """
    model = Post
    fields = ['title', 'slug', 'content', 'excerpt', 'category', 'tags', 'featured']
    template_name = 'blog/post_form.html'
    
    def form_valid(self, form):
        """Set the author to current user"""
        form.instance.author = self.request.user
        messages.success(self.request, 'Post created successfully!')
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing post (only by author)
    Demonstrates: UpdateView, permission checking
    """
    model = Post
    fields = ['title', 'slug', 'content', 'excerpt', 'category', 'tags', 'featured', 'status']
    template_name = 'blog/post_form.html'
    
    def get_queryset(self):
        """Only allow authors to edit their own posts"""
        return Post.objects.filter(author=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)

# =============================================================================
# UTILITY VIEWS
# =============================================================================

def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    return render(request, 'errors/500.html', status=500)

def about(request):
    """Simple about page"""
    context = {
        'page_title': 'About Us',
        'total_posts': Post.objects.filter(status='published').count(),
        'total_categories': Category.objects.count(),
    }
    return render(request, 'blog/about.html', context)