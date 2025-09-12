"""
API views for the blog application.
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Post, Category, Tag, Comment, Like
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CategorySerializer, TagSerializer, CommentSerializer, 
    CommentCreateUpdateSerializer, LikeSerializer
)
from .permissions import IsAuthorOrReadOnly, IsCommentAuthorOrReadOnly, IsAdminOrReadOnly


@extend_schema_view(
    list=extend_schema(description="List all categories"),
    create=extend_schema(description="Create a new category"),
    retrieve=extend_schema(description="Get a specific category"),
    update=extend_schema(description="Update a category"),
    destroy=extend_schema(description="Delete a category"),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get all posts in this category."""
        category = self.get_object()
        posts = Post.objects.filter(category=category, status='published')
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="List all tags"),
    create=extend_schema(description="Create a new tag"),
    retrieve=extend_schema(description="Get a specific tag"),
    update=extend_schema(description="Update a tag"),
    destroy=extend_schema(description="Delete a tag"),
)
class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get all posts with this tag."""
        tag = self.get_object()
        posts = Post.objects.filter(tags=tag, status='published')
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="List all posts with filtering and search"),
    create=extend_schema(description="Create a new post"),
    retrieve=extend_schema(description="Get a specific post"),
    update=extend_schema(description="Update a post"),
    destroy=extend_schema(description="Delete a post"),
)
class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog posts.
    
    Provides CRUD operations plus custom actions for publishing,
    liking, and filtering posts.
    """
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'excerpt']
    filterset_fields = ['category', 'tags', 'status', 'author']
    ordering_fields = ['created_at', 'updated_at', 'title', 'views_count']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter queryset based on user permissions.
        Anonymous users and non-authors can only see published posts.
        """
        queryset = Post.objects.select_related('author', 'category').prefetch_related('tags')
        
        if self.request.user.is_authenticated:
            # Authenticated users can see their own drafts
            if self.action in ['list', 'my_posts']:
                return queryset.filter(
                    Q(status='published') | Q(author=self.request.user)
                )
            return queryset
        else:
            # Anonymous users can only see published posts
            return queryset.filter(status='published')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def perform_create(self, serializer):
        """Set the author to the current user when creating a post."""
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Increment view count when retrieving a post."""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(description="Publish a draft post")
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a draft post."""
        post = self.get_object()
        if post.status != 'draft':
            return Response(
                {'error': 'Only draft posts can be published'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.status = 'published'
        post.published_at = timezone.now()
        post.save()
        
        serializer = self.get_serializer(post)
        return Response(serializer.data)

    @extend_schema(description="Unpublish a published post")
    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Unpublish a published post."""
        post = self.get_object()
        if post.status != 'published':
            return Response(
                {'error': 'Only published posts can be unpublished'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        post.status = 'draft'
        post.save()
        
        serializer = self.get_serializer(post)
        return Response(serializer.data)

    @extend_schema(description="Get only published posts")
    @action(detail=False, methods=['get'])
    def published(self, request):
        """Get only published posts."""
        published_posts = self.get_queryset().filter(status='published')
        page = self.paginate_queryset(published_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(published_posts, many=True)
        return Response(serializer.data)

    @extend_schema(description="Get posts by the current user")
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_posts(self, request):
        """Get posts by the current user."""
        user_posts = Post.objects.filter(author=request.user)
        page = self.paginate_queryset(user_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(user_posts, many=True)
        return Response(serializer.data)

    @extend_schema(description="Like or unlike a post")
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Like or unlike a post."""
        post = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user, 
            post=post
        )
        
        if not created:
            like.delete()
            return Response({'status': 'unliked'})
        
        return Response({'status': 'liked'})

    @extend_schema(description="Get post statistics")
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a post."""
        post = self.get_object()
        stats = {
            'views_count': post.views_count,
            'likes_count': post.likes.count(),
            'comments_count': post.comments.filter(is_approved=True).count(),
            'word_count': len(post.content.split()),
            'reading_time': max(1, round(len(post.content.split()) / 200))
        }
        return Response(stats)


@extend_schema_view(
    list=extend_schema(description="List comments for a post"),
    create=extend_schema(description="Create a new comment"),
    retrieve=extend_schema(description="Get a specific comment"),
    update=extend_schema(description="Update a comment"),
    destroy=extend_schema(description="Delete a comment"),
)
class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments on blog posts.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCommentAuthorOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        """Filter comments by post."""
        post_id = self.kwargs.get('post_pk')
        return Comment.objects.filter(
            post_id=post_id, 
            is_approved=True
        ).select_related('author', 'post')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateUpdateSerializer
        return CommentSerializer

    def get_serializer_context(self):
        """Add post_id to serializer context."""
        context = super().get_serializer_context()
        context['post_id'] = int(self.kwargs.get('post_pk'))
        return context

    def perform_create(self, serializer):
        """Set the author and post when creating a comment."""
        post = get_object_or_404(Post, pk=self.kwargs.get('post_pk'))
        serializer.save(author=self.request.user, post=post)

    @extend_schema(description="Like or unlike a comment")
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, post_pk=None, pk=None):
        """Like or unlike a comment."""
        comment = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user, 
            comment=comment
        )
        
        if not created:
            like.delete()
            return Response({'status': 'unliked'})
        
        return Response({'status': 'liked'})

    @extend_schema(description="Get replies to a comment")
    @action(detail=True, methods=['get'])
    def replies(self, request, post_pk=None, pk=None):
        """Get replies to a comment."""
        comment = self.get_object()
        replies = comment.replies.filter(is_approved=True)
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)