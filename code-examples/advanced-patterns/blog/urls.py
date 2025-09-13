"""
URL configuration for blog app.
"""
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('api/posts/', views.PostAPIView.as_view(), name='api_post_list'),
    path('api/posts/<int:pk>/', views.PostDetailAPIView.as_view(), name='api_post_detail'),
    path('api/posts/<int:pk>/like/', views.LikePostAPIView.as_view(), name='api_like_post'),
    path('api/posts/<int:pk>/share/', views.SharePostAPIView.as_view(), name='api_share_post'),
]