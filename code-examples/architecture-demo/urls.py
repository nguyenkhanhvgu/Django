# Django Architecture Demo - URL Configuration
# This file demonstrates Django URL routing patterns

from django.urls import path, re_path
from . import views

app_name = 'blog'

urlpatterns = [
    # =============================================================================
    # FUNCTION-BASED VIEW URLS
    # =============================================================================
    
    # Home page - list all posts
    path('', views.post_list, name='post_list'),
    
    # Post detail by slug
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # Category detail
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    
    # Search functionality
    path('search/', views.search_posts, name='search_posts'),
    
    # Comment functionality (requires login)
    path('post/<slug:post_slug>/comment/', views.add_comment, name='add_comment'),
    
    # API endpoints
    path('api/posts/', views.api_post_list, name='api_post_list'),
    
    # Static pages
    path('about/', views.about, name='about'),
    
    # =============================================================================
    # CLASS-BASED VIEW URLS
    # =============================================================================
    
    # Alternative post list using CBV
    path('cbv/posts/', views.PostListView.as_view(), name='post_list_cbv'),
    
    # Alternative post detail using CBV
    path('cbv/post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail_cbv'),
    
    # Category list
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    
    # Post management (requires login)
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_update'),
    
    # =============================================================================
    # ADVANCED URL PATTERNS
    # =============================================================================
    
    # Archive by year
    re_path(r'^archive/(?P<year>[0-9]{4})/$', views.post_list, name='posts_by_year'),
    
    # Archive by year and month
    re_path(
        r'^archive/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', 
        views.post_list, 
        name='posts_by_month'
    ),
    
    # Tag-based filtering (alternative approach)
    path('tag/<int:tag_id>/', views.post_list, name='posts_by_tag'),
    
    # RSS feed (would require additional implementation)
    path('feed/', views.post_list, name='rss_feed'),
    
    # Sitemap (would require additional implementation)
    path('sitemap.xml', views.post_list, name='sitemap'),
]

# =============================================================================
# URL PATTERN EXAMPLES AND EXPLANATIONS
# =============================================================================

"""
URL Pattern Types and Examples:

1. Basic string patterns:
   path('about/', views.about, name='about')
   - Matches: /about/
   - Parameters: None

2. Integer parameters:
   path('category/<int:pk>/', views.category_detail, name='category_detail')
   - Matches: /category/1/, /category/123/
   - Parameters: pk (integer)

3. Slug parameters:
   path('post/<slug:slug>/', views.post_detail, name='post_detail')
   - Matches: /post/my-first-post/, /post/django-tutorial/
   - Parameters: slug (letters, numbers, hyphens, underscores)

4. String parameters:
   path('user/<str:username>/', views.user_profile, name='user_profile')
   - Matches: /user/john/, /user/jane_doe/
   - Parameters: username (any string except '/')

5. UUID parameters:
   path('item/<uuid:item_id>/', views.item_detail, name='item_detail')
   - Matches: /item/550e8400-e29b-41d4-a716-446655440000/
   - Parameters: item_id (UUID format)

6. Path parameters:
   path('files/<path:file_path>/', views.serve_file, name='serve_file')
   - Matches: /files/documents/report.pdf, /files/images/photo.jpg
   - Parameters: file_path (any string including '/')

7. Regular expression patterns:
   re_path(r'^archive/(?P<year>[0-9]{4})/$', views.posts_by_year)
   - Matches: /archive/2024/, /archive/2023/
   - Parameters: year (4-digit number)

8. Optional parameters with defaults:
   path('posts/', views.post_list, {'page': 1}, name='post_list_default')
   path('posts/page/<int:page>/', views.post_list, name='post_list_paged')
   - First pattern provides default page=1
   - Second pattern accepts page parameter

9. Multiple parameters:
   path('category/<int:cat_id>/post/<slug:slug>/', views.category_post)
   - Matches: /category/1/post/my-post/
   - Parameters: cat_id (integer), slug (slug)

10. Nested URL includes:
    # In main urls.py
    path('blog/', include('blog.urls')),
    # In blog/urls.py
    path('post/<slug:slug>/', views.post_detail)
    # Final URL: /blog/post/my-post/

URL Naming and Reversing:
- Always use 'name' parameter for URL patterns
- Use {% url 'name' %} in templates
- Use reverse('name') in views
- Use app_name for namespacing: {% url 'blog:post_detail' slug=post.slug %}

Best Practices:
1. Use descriptive names for URL patterns
2. Keep URLs simple and readable
3. Use slugs for SEO-friendly URLs
4. Group related URLs together
5. Use namespacing for apps
6. Avoid hardcoding URLs in templates and views
7. Use trailing slashes consistently
8. Order patterns from most specific to least specific
"""