# Django REST Framework Tutorial

## Introduction

Django REST Framework (DRF) is a powerful toolkit for building Web APIs in Django. It provides a flexible, feature-rich framework that makes it easy to build REST APIs with minimal code while maintaining best practices for security, serialization, and authentication.

## What You'll Learn

By the end of this tutorial, you'll be able to:
- Set up Django REST Framework in a Django project
- Create serializers to convert Django models to JSON
- Build API views using viewsets and generic views
- Implement authentication and permissions
- Test your APIs effectively
- Generate API documentation

## Prerequisites

Before starting this tutorial, you should be familiar with:
- Django basics (models, views, URLs)
- HTTP methods (GET, POST, PUT, DELETE)
- JSON format
- Basic understanding of REST principles

## Setting Up Django REST Framework

### Installation

First, install Django REST Framework in your virtual environment:

```bash
pip install djangorestframework
pip install markdown  # For browsable API docs
pip install django-filter  # For filtering support
```

### Django Settings Configuration

Add DRF to your Django settings:

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # Add this
    'rest_framework.authtoken',  # For token authentication
    'django_filters',  # For filtering
    'your_app_name',
]

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

### URL Configuration

Add DRF URLs to your main URL configuration:

```python
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('your_app.urls')),
    path('api-auth/', include('rest_framework.urls')),  # For browsable API login
]
```

## Understanding Serializers

Serializers in DRF are similar to Django forms but for APIs. They handle converting complex data types (like Django model instances) to Python data types that can be easily rendered into JSON, XML, or other content types.

### Basic Serializer Example

Let's start with a simple blog model:

```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
```

Now create serializers for these models:

```python
# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'category', 
            'category_id', 'created_at', 'updated_at', 'published'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_title(self, value):
        """Custom validation for title field"""
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long")
        return value

class PostCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating posts"""
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'published']
```

### Serializer Field Types and Options

DRF provides many field types for different data types:

```python
# Advanced serializer example
class AdvancedPostSerializer(serializers.ModelSerializer):
    # Custom fields
    author_name = serializers.CharField(source='author.username', read_only=True)
    word_count = serializers.SerializerMethodField()
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    
    # Nested serialization
    comments = serializers.StringRelatedMany(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = '__all__'
    
    def get_word_count(self, obj):
        """Calculate word count for the post content"""
        return len(obj.content.split())
    
    def validate(self, data):
        """Object-level validation"""
        if data.get('published') and not data.get('content'):
            raise serializers.ValidationError("Published posts must have content")
        return data
```

## Building API Views with ViewSets

ViewSets provide a way to group related views together and automatically generate URL patterns.

### ModelViewSet Example

```python
# views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Category
from .serializers import PostSerializer, CategorySerializer, PostCreateSerializer
from .permissions import IsAuthorOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['name']

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    filterset_fields = ['category', 'published', 'author']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return different serializers for different actions"""
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        """Set the author to the current user when creating a post"""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Custom action to publish a post"""
        post = self.get_object()
        post.published = True
        post.save()
        return Response({'status': 'post published'})

    @action(detail=False)
    def published(self, request):
        """Custom action to get only published posts"""
        published_posts = Post.objects.filter(published=True)
        serializer = self.get_serializer(published_posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """Get posts by the current user"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        user_posts = Post.objects.filter(author=request.user)
        serializer = self.get_serializer(user_posts, many=True)
        return Response(serializer.data)
```

### Generic Views Alternative

For more control, you can use generic views instead of viewsets:

```python
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
```

## Authentication and Permissions

### Custom Permissions

Create custom permission classes for fine-grained access control:

```python
# permissions.py
from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of a post to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for the author
        return obj.author == request.user

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

### Token Authentication Setup

```python
# In your Django app's management/commands/create_tokens.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Create tokens for all users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            Token.objects.get_or_create(user=user)
        self.stdout.write('Tokens created for all users')
```

Run migrations to create token tables:

```bash
python manage.py migrate
python manage.py create_tokens
```

### Using Authentication in Views

```python
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({'message': 'Hello, authenticated user!'})
```

## URL Configuration for APIs

Create URL patterns for your API:

```python
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Using routers with viewsets
router = DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'categories', views.CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Alternative: manual URL patterns for generic views
    # path('posts/', views.PostListCreateView.as_view(), name='post-list'),
    # path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
]
```

## Testing Your API

### Using Django's Test Framework

```python
# tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Post, Category

class PostAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.category = Category.objects.create(
            name='Test Category',
            description='Test description'
        )
        
    def test_create_post_authenticated(self):
        """Test creating a post with authentication"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            'title': 'Test Post',
            'content': 'This is a test post content',
            'category': self.category.id,
            'published': True
        }
        response = self.client.post('/api/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        
    def test_create_post_unauthenticated(self):
        """Test creating a post without authentication"""
        data = {
            'title': 'Test Post',
            'content': 'This is a test post content',
            'category': self.category.id
        }
        response = self.client.post('/api/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_posts_list(self):
        """Test retrieving posts list"""
        Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            category=self.category
        )
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
```

### Using pytest-django (Alternative)

```python
# test_api.py
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

@pytest.mark.django_db
class TestPostAPI:
    def test_create_post(self):
        client = APIClient()
        user = User.objects.create_user(username='test', password='test')
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = client.post('/api/posts/', {
            'title': 'Test Post',
            'content': 'Test content'
        })
        assert response.status_code == status.HTTP_201_CREATED
```

## API Documentation

### Using DRF's Built-in Documentation

DRF provides automatic API documentation. Add to your URLs:

```python
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('docs/', include_docs_urls(title='Blog API')),
    # ... other patterns
]
```

### Using drf-spectacular for OpenAPI

Install and configure drf-spectacular for better documentation:

```bash
pip install drf-spectacular
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    # ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Blog API',
    'DESCRIPTION': 'A comprehensive blog API built with Django REST Framework',
    'VERSION': '1.0.0',
}
```

```python
# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # ... other patterns
]
```

## Best Practices

### 1. Versioning Your API

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
}

# urls.py
urlpatterns = [
    path('api/v1/', include('myapp.urls')),
]
```

### 2. Pagination

```python
# Custom pagination
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
```

### 3. Error Handling

```python
# Custom exception handler
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': {
                'status_code': response.status_code,
                'message': response.data
            }
        }
        response.data = custom_response_data
    
    return response
```

### 4. Throttling

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}
```

## Next Steps

After completing this tutorial, you should explore:

1. **Advanced Authentication**: JWT tokens, OAuth2
2. **File Uploads**: Handling file uploads in APIs
3. **Caching**: Implementing caching strategies
4. **API Monitoring**: Using tools like Django Debug Toolbar
5. **Production Deployment**: CORS, security headers, rate limiting

## Common Troubleshooting

### CORS Issues
Install django-cors-headers:
```bash
pip install django-cors-headers
```

### Authentication Problems
- Check token format: `Token <your-token>`
- Verify user permissions
- Check authentication classes in settings

### Serialization Errors
- Validate required fields
- Check field types match model fields
- Review custom validation methods

This tutorial provides a solid foundation for building REST APIs with Django REST Framework. Practice with the exercises in the next section to reinforce these concepts.