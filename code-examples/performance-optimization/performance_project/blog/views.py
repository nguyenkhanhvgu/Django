"""
Blog views with performance optimization examples.
"""

import asyncio
import aiohttp
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic import ListView, DetailView
from django.db.models import Count, Prefetch, Q
from django.utils.decorators import method_decorator
from asgiref.sync import sync_to_async
from .models import Post, Category, Author, Comment
from utils.cache_helpers import CacheHelper
from utils.profiling import QueryProfiler


# Function-based views with caching

@cache_page(60 * 15)  # Cache for 15 minutes
@vary_on_headers('User-Agent')
def post_list_cached(request):
    """Cached post list view."""
    posts = Post.objects.published().optimized()
    
    # Paginate results
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
    })


def post_list_manual_cache(request):
    """Post list with manual cache control."""
    page = request.GET.get('page', 1)
    cache_key = f"post_list_page_{page}"
    
    # Try to get from cache
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'blog/post_list.html', cached_data)
    
    # If not in cache, generate data
    with QueryProfiler():
        posts = Post.objects.published().optimized()
        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page)
        
        context = {
            'page_obj': page_obj,
            'posts': page_obj.object_list,
        }
        
        # Cache for 15 minutes
        cache.set(cache_key, context, 60 * 15)
        
        return render(request, 'blog/post_list.html', context)


def post_detail_optimized(request, slug):
    """Optimized post detail view."""
    cache_key = f"post_detail_{slug}"
    
    # Try cache first
    post = cache.get(cache_key)
    if not post:
        # Optimize query with select_related and prefetch_related
        post = get_object_or_404(
            Post.objects.select_related('author__user')
                       .prefetch_related('categories', 'tags')
                       .prefetch_related(
                           Prefetch(
                               'comments',
                               queryset=Comment.objects.filter(is_approved=True)
                                              .select_related('post')
                                              .order_by('-created_at')
                           )
                       ),
            slug=slug,
            status='published'
        )
        
        # Cache for 30 minutes
        cache.set(cache_key, post, 60 * 30)
    
    # Track view (async to avoid blocking)
    track_post_view.delay(post.id, request.META.get('REMOTE_ADDR'))
    
    # Get related posts efficiently
    related_posts = Post.objects.published()\
                               .filter(categories__in=post.categories.all())\
                               .exclude(id=post.id)\
                               .distinct()[:5]
    
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'related_posts': related_posts,
    })


def category_posts(request, slug):
    """Category posts with optimization."""
    category = get_object_or_404(Category, slug=slug)
    
    cache_key = f"category_posts_{slug}_{request.GET.get('page', 1)}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return render(request, 'blog/category_posts.html', cached_data)
    
    # Optimized query
    posts = Post.objects.published()\
                       .filter(categories=category)\
                       .optimized()\
                       .distinct()
    
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
    }
    
    # Cache for 10 minutes
    cache.set(cache_key, context, 60 * 10)
    
    return render(request, 'blog/category_posts.html', context)


# Class-based views with optimization

@method_decorator(cache_page(60 * 20), name='dispatch')
class OptimizedPostListView(ListView):
    """Optimized ListView for posts."""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Return optimized queryset."""
        return Post.objects.published().optimized()
    
    def get_context_data(self, **kwargs):
        """Add additional context with caching."""
        context = super().get_context_data(**kwargs)
        
        # Cache popular posts
        popular_posts = cache.get('popular_posts')
        if not popular_posts:
            popular_posts = Post.objects.published()\
                                       .order_by('-view_count')[:5]
            cache.set('popular_posts', popular_posts, 60 * 60)  # 1 hour
        
        context['popular_posts'] = popular_posts
        return context


class OptimizedPostDetailView(DetailView):
    """Optimized DetailView for posts."""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    
    def get_queryset(self):
        """Return optimized queryset."""
        return Post.objects.published().optimized()
    
    def get_object(self, queryset=None):
        """Get object with caching."""
        if queryset is None:
            queryset = self.get_queryset()
        
        slug = self.kwargs.get(self.slug_url_kwarg)
        cache_key = f"post_detail_obj_{slug}"
        
        obj = cache.get(cache_key)
        if not obj:
            obj = get_object_or_404(queryset, slug=slug)
            cache.set(cache_key, obj, 60 * 30)  # 30 minutes
        
        return obj


# API views with performance optimization

def api_posts_list(request):
    """API endpoint for posts with optimization."""
    cache_key = CacheHelper.cache_key_from_request(request, "api_posts")
    
    def get_posts_data():
        posts = Post.objects.published()\
                           .select_related('author__user')\
                           .values(
                               'id', 'title', 'slug', 'excerpt',
                               'published_at', 'author__user__username'
                           )[:20]
        return list(posts)
    
    posts_data = CacheHelper.get_or_set_complex_data(
        cache_key, get_posts_data, 60 * 10
    )
    
    return JsonResponse({'posts': posts_data})


def api_post_stats(request):
    """API endpoint for post statistics."""
    cache_key = "post_stats"
    
    stats = cache.get(cache_key)
    if not stats:
        # Use aggregation for better performance
        stats = {
            'total_posts': Post.objects.published().count(),
            'total_authors': Author.objects.count(),
            'total_categories': Category.objects.count(),
            'posts_by_category': list(
                Category.objects.annotate(
                    post_count=Count('posts', filter=Q(posts__status='published'))
                ).values('name', 'post_count')
            ),
            'top_authors': list(
                Author.objects.annotate(
                    post_count=Count('posts', filter=Q(posts__status='published'))
                ).filter(post_count__gt=0)
                .order_by('-post_count')[:5]
                .values('user__username', 'post_count')
            )
        }
        
        # Cache for 1 hour
        cache.set(cache_key, stats, 60 * 60)
    
    return JsonResponse(stats)


# Async views for I/O bound operations

async def async_external_data_view(request):
    """Async view for fetching external data."""
    
    async def fetch_external_api(url):
        """Fetch data from external API."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()
    
    # Make multiple API calls concurrently
    tasks = [
        fetch_external_api('https://jsonplaceholder.typicode.com/posts/1'),
        fetch_external_api('https://jsonplaceholder.typicode.com/posts/2'),
        fetch_external_api('https://jsonplaceholder.typicode.com/posts/3'),
    ]
    
    try:
        external_data = await asyncio.gather(*tasks)
    except Exception as e:
        external_data = []
    
    # Async database operations
    posts = await sync_to_async(list)(
        Post.objects.published().optimized()[:5]
    )
    
    return JsonResponse({
        'external_data': external_data,
        'local_posts': [
            {
                'title': post.title,
                'slug': post.slug,
                'author': post.author.user.username
            }
            for post in posts
        ]
    })


# Search view with optimization

def search_posts(request):
    """Search posts with caching and optimization."""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'blog/search.html', {'posts': []})
    
    # Cache search results
    cache_key = f"search_{hash(query)}_{request.GET.get('page', 1)}"
    cached_results = cache.get(cache_key)
    
    if cached_results:
        return render(request, 'blog/search.html', cached_results)
    
    # Perform search with optimization
    posts = Post.objects.published()\
                       .filter(
                           Q(title__icontains=query) |
                           Q(content__icontains=query) |
                           Q(excerpt__icontains=query)
                       )\
                       .optimized()\
                       .distinct()
    
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'posts': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
    }
    
    # Cache search results for 5 minutes
    cache.set(cache_key, context, 60 * 5)
    
    return render(request, 'blog/search.html', context)


# Utility functions

def track_post_view(post_id, ip_address):
    """Track post view asynchronously."""
    from .models import PostView
    try:
        PostView.objects.create(
            post_id=post_id,
            ip_address=ip_address or '127.0.0.1'
        )
        # Update post view count
        Post.objects.filter(id=post_id).update(
            view_count=models.F('view_count') + 1
        )
    except Exception:
        # Silently fail to avoid breaking the main request
        pass


def invalidate_post_caches(post_slug):
    """Invalidate all caches related to a post."""
    cache_keys = [
        f"post_detail_{post_slug}",
        f"post_detail_obj_{post_slug}",
        "post_stats",
        "popular_posts",
    ]
    
    cache.delete_many(cache_keys)
    
    # Invalidate list caches
    CacheHelper.invalidate_related_cache("post_list")
    CacheHelper.invalidate_related_cache("category_posts")