"""
URL configuration for the blog API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)

# Manual URL patterns for nested resources
urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:post_pk>/comments/', views.CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='post-comments-list'),
    path('posts/<int:post_pk>/comments/<int:pk>/', views.CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='post-comments-detail'),
    path('posts/<int:post_pk>/comments/<int:pk>/like/', views.CommentViewSet.as_view({
        'post': 'like'
    }), name='post-comments-like'),
    path('posts/<int:post_pk>/comments/<int:pk>/replies/', views.CommentViewSet.as_view({
        'get': 'replies'
    }), name='post-comments-replies'),
]