# Advanced Django Patterns

## Table of Contents
1. [Custom Middleware Development](#custom-middleware-development)
2. [Django Signals and Event-Driven Architecture](#django-signals-and-event-driven-architecture)
3. [Advanced ORM Techniques and Custom Managers](#advanced-orm-techniques-and-custom-managers)
4. [Django-Specific Design Patterns](#django-specific-design-patterns)

## Custom Middleware Development

### Understanding Django Middleware

Middleware in Django is a framework of hooks into Django's request/response processing. It's a light, low-level "plugin" system for globally altering Django's input or output.

### Creating Custom Middleware

#### Basic Middleware Structure

```python
# middleware/custom_middleware.py
class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        
        response = self.get_response(request)
        
        # Code to be executed for each request/response after
        # the view is called.
        
        return response
```

#### Request Logging Middleware

```python
# middleware/logging_middleware.py
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Log request details
        logger.info(f"Request: {request.method} {request.path}")
        
        response = self.get_response(request)
        
        # Log response details
        duration = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {duration:.2f}s")
        
        return response
```

#### Authentication Middleware

```python
# middleware/auth_middleware.py
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser

class APIAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip authentication for certain paths
        if request.path.startswith('/api/public/'):
            return self.get_response(request)
        
        # Check for API key in headers
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return JsonResponse({'error': 'API key required'}, status=401)
        
        # Validate API key (simplified example)
        if not self.validate_api_key(api_key):
            return JsonResponse({'error': 'Invalid API key'}, status=401)
        
        response = self.get_response(request)
        return response
    
    def validate_api_key(self, api_key):
        # Implement your API key validation logic
        return api_key == 'your-secret-api-key'
```

#### Rate Limiting Middleware

```python
# middleware/rate_limit_middleware.py
from django.core.cache import cache
from django.http import HttpResponse
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 100  # requests per minute
        self.window = 60  # seconds

    def __call__(self, request):
        client_ip = self.get_client_ip(request)
        cache_key = f"rate_limit_{client_ip}"
        
        # Get current request count
        requests = cache.get(cache_key, [])
        now = time.time()
        
        # Remove old requests outside the window
        requests = [req_time for req_time in requests if now - req_time < self.window]
        
        # Check if rate limit exceeded
        if len(requests) >= self.rate_limit:
            return HttpResponse("Rate limit exceeded", status=429)
        
        # Add current request
        requests.append(now)
        cache.set(cache_key, requests, self.window)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

### Middleware Configuration

Add your middleware to `settings.py`:

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'middleware.logging_middleware.RequestLoggingMiddleware',
    'middleware.rate_limit_middleware.RateLimitMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.auth_middleware.APIAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

## Django Signals and Event-Driven Architecture

### Understanding Django Signals

Django signals allow certain senders to notify a set of receivers when some actions have taken place. They're useful for allowing decoupled applications to get notified when actions occur elsewhere in the framework.

### Built-in Signals

#### Model Signals

```python
# signals/handlers.py
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, AuditLog

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved."""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

@receiver(pre_save, sender=User)
def log_user_changes(sender, instance, **kwargs):
    """Log changes to user objects."""
    if instance.pk:  # Only for existing users
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.email != instance.email:
                AuditLog.objects.create(
                    action='email_changed',
                    user=instance,
                    old_value=old_instance.email,
                    new_value=instance.email
                )
        except User.DoesNotExist:
            pass

@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """Log when a user is deleted."""
    AuditLog.objects.create(
        action='user_deleted',
        user_id=instance.pk,
        details=f"User {instance.username} was deleted"
    )
```

#### Request/Response Signals

```python
# signals/request_handlers.py
from django.core.signals import request_started, request_finished
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(request_started)
def log_request_started(sender, environ, **kwargs):
    """Log when a request starts."""
    logger.info(f"Request started: {environ.get('REQUEST_METHOD')} {environ.get('PATH_INFO')}")

@receiver(request_finished)
def log_request_finished(sender, **kwargs):
    """Log when a request finishes."""
    logger.info("Request finished")
```

### Custom Signals

#### Creating Custom Signals

```python
# signals/custom_signals.py
import django.dispatch

# Define custom signals
user_logged_in_successfully = django.dispatch.Signal()
order_status_changed = django.dispatch.Signal()
payment_processed = django.dispatch.Signal()

# Example usage in views
from django.contrib.auth import authenticate, login
from .signals.custom_signals import user_logged_in_successfully

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Send custom signal
            user_logged_in_successfully.send(
                sender=user.__class__,
                user=user,
                request=request
            )
            return redirect('dashboard')
    
    return render(request, 'login.html')
```

#### Signal Handlers for Custom Signals

```python
# signals/custom_handlers.py
from django.dispatch import receiver
from .custom_signals import user_logged_in_successfully, order_status_changed
from .models import LoginHistory, Notification

@receiver(user_logged_in_successfully)
def track_user_login(sender, user, request, **kwargs):
    """Track user login for analytics."""
    LoginHistory.objects.create(
        user=user,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )

@receiver(user_logged_in_successfully)
def send_login_notification(sender, user, request, **kwargs):
    """Send notification on successful login."""
    if user.profile.login_notifications_enabled:
        Notification.objects.create(
            user=user,
            message=f"Successful login from {request.META.get('REMOTE_ADDR')}",
            type='security'
        )

@receiver(order_status_changed)
def handle_order_status_change(sender, order, old_status, new_status, **kwargs):
    """Handle order status changes."""
    if new_status == 'shipped':
        # Send shipping notification
        send_shipping_notification(order)
    elif new_status == 'delivered':
        # Request review
        request_product_review(order)
```

### Signal Best Practices

#### Avoiding Circular Imports

```python
# apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        import myapp.signals.handlers  # Import signal handlers
```

#### Error Handling in Signals

```python
# signals/safe_handlers.py
from django.dispatch import receiver
from django.db.models.signals import post_save
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def safe_signal_handler(sender, instance, **kwargs):
    """Signal handler with proper error handling."""
    try:
        # Your signal logic here
        process_user_data(instance)
    except Exception as e:
        logger.error(f"Error in signal handler: {e}")
        # Don't re-raise the exception to avoid breaking the main flow
```

## Advanced ORM Techniques and Custom Managers

### Custom Managers

#### Basic Custom Manager

```python
# models.py
from django.db import models

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = models.Manager()  # Default manager
    published = PublishedManager()  # Custom manager

# Usage
published_posts = Post.published.all()
```

#### Advanced Custom Manager with Methods

```python
# models.py
class PostManager(models.Manager):
    def published(self):
        return self.filter(status='published')
    
    def by_author(self, author):
        return self.filter(author=author)
    
    def recent(self, days=7):
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def popular(self, min_views=100):
        return self.filter(view_count__gte=min_views)
    
    def with_comments(self):
        return self.annotate(
            comment_count=models.Count('comments')
        ).filter(comment_count__gt=0)

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='draft')
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = PostManager()

# Usage
recent_popular_posts = Post.objects.recent().popular().published()
posts_with_comments = Post.objects.with_comments().order_by('-comment_count')
```

### Custom QuerySets

#### Creating Custom QuerySets

```python
# models.py
class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status='published')
    
    def by_author(self, author):
        return self.filter(author=author)
    
    def recent(self, days=7):
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def with_author_info(self):
        return self.select_related('author')
    
    def with_comment_count(self):
        return self.annotate(comment_count=models.Count('comments'))

class PostManager(models.Manager):
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def recent(self, days=7):
        return self.get_queryset().recent(days)

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = PostManager()

# Usage - methods can be chained
recent_published_posts = Post.objects.recent().published().with_author_info()
```

### Advanced Query Techniques

#### Complex Annotations and Aggregations

```python
# Advanced query examples
from django.db.models import Count, Avg, Sum, F, Q, Case, When, Value
from django.db.models.functions import Coalesce, Extract

# Complex annotations
posts_with_stats = Post.objects.annotate(
    comment_count=Count('comments'),
    avg_rating=Avg('ratings__score'),
    total_likes=Sum('likes__count'),
    days_since_published=Extract('now', 'day') - Extract('created_at', 'day')
).filter(comment_count__gt=5)

# Conditional annotations
posts_with_status = Post.objects.annotate(
    popularity=Case(
        When(view_count__gte=1000, then=Value('High')),
        When(view_count__gte=100, then=Value('Medium')),
        default=Value('Low'),
        output_field=models.CharField()
    )
)

# Complex filtering with Q objects
complex_filter = Post.objects.filter(
    Q(title__icontains='django') | Q(content__icontains='django'),
    Q(status='published') & Q(created_at__year=2024)
)
```

#### Custom Database Functions

```python
# utils/db_functions.py
from django.db.models import Func

class Round(Func):
    function = 'ROUND'
    arity = 2

class Substring(Func):
    function = 'SUBSTRING'
    
    def __init__(self, expression, start, length=None, **extra):
        if length is not None:
            super().__init__(expression, start, length, **extra)
        else:
            super().__init__(expression, start, **extra)

# Usage
from .utils.db_functions import Round, Substring

posts_with_rounded_rating = Post.objects.annotate(
    rounded_rating=Round('average_rating', 1)
)

posts_with_excerpt = Post.objects.annotate(
    excerpt=Substring('content', 1, 100)
)
```

### Raw SQL and Custom SQL

#### Using Raw SQL Safely

```python
# models.py
class PostManager(models.Manager):
    def posts_with_recent_comments(self, days=7):
        """Get posts with comments from the last N days using raw SQL."""
        return self.raw("""
            SELECT DISTINCT p.*
            FROM myapp_post p
            INNER JOIN myapp_comment c ON p.id = c.post_id
            WHERE c.created_at >= %s
            ORDER BY p.created_at DESC
        """, [timezone.now() - timedelta(days=days)])
    
    def popular_posts_by_month(self):
        """Get popular posts grouped by month."""
        return self.raw("""
            SELECT 
                id,
                title,
                EXTRACT(YEAR FROM created_at) as year,
                EXTRACT(MONTH FROM created_at) as month,
                COUNT(*) as post_count
            FROM myapp_post
            WHERE status = 'published'
            GROUP BY EXTRACT(YEAR FROM created_at), EXTRACT(MONTH FROM created_at), id, title
            ORDER BY year DESC, month DESC, post_count DESC
        """)
```

#### Custom SQL with Extra()

```python
# Using extra() for complex queries
posts_with_custom_ordering = Post.objects.extra(
    select={
        'comment_count': 'SELECT COUNT(*) FROM myapp_comment WHERE post_id = myapp_post.id',
        'days_old': 'EXTRACT(days FROM (NOW() - created_at))'
    },
    where=["status = %s"],
    params=['published'],
    order_by=['-comment_count', 'days_old']
)
```

## Django-Specific Design Patterns

### Repository Pattern

#### Basic Repository Implementation

```python
# repositories/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from django.db.models import Model, QuerySet

class BaseRepository(ABC):
    """Abstract base repository."""
    
    @abstractmethod
    def get_all(self) -> QuerySet:
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Model]:
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> Model:
        pass
    
    @abstractmethod
    def update(self, instance: Model, **kwargs) -> Model:
        pass
    
    @abstractmethod
    def delete(self, instance: Model) -> None:
        pass

# repositories/post_repository.py
from .base import BaseRepository
from ..models import Post

class PostRepository(BaseRepository):
    def __init__(self):
        self.model = Post
    
    def get_all(self):
        return self.model.objects.all()
    
    def get_by_id(self, id: int):
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)
    
    def update(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance):
        instance.delete()
    
    # Domain-specific methods
    def get_published_posts(self):
        return self.model.objects.filter(status='published')
    
    def get_posts_by_author(self, author):
        return self.model.objects.filter(author=author)
    
    def get_recent_posts(self, days=7):
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.model.objects.filter(created_at__gte=cutoff_date)
```

#### Using Repository in Views

```python
# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .repositories.post_repository import PostRepository

class PostView:
    def __init__(self):
        self.post_repository = PostRepository()
    
    def list_posts(self, request):
        posts = self.post_repository.get_published_posts()
        return render(request, 'posts/list.html', {'posts': posts})
    
    def post_detail(self, request, post_id):
        post = self.post_repository.get_by_id(post_id)
        if not post:
            return JsonResponse({'error': 'Post not found'}, status=404)
        return render(request, 'posts/detail.html', {'post': post})
    
    def create_post(self, request):
        if request.method == 'POST':
            post_data = {
                'title': request.POST.get('title'),
                'content': request.POST.get('content'),
                'author': request.user
            }
            post = self.post_repository.create(**post_data)
            return JsonResponse({'id': post.id, 'title': post.title})
        
        return render(request, 'posts/create.html')
```

### Service Layer Pattern

#### Service Layer Implementation

```python
# services/base_service.py
class BaseService:
    """Base service class with common functionality."""
    
    def __init__(self, repository):
        self.repository = repository
    
    def get_all(self):
        return self.repository.get_all()
    
    def get_by_id(self, id):
        return self.repository.get_by_id(id)

# services/post_service.py
from .base_service import BaseService
from ..repositories.post_repository import PostRepository
from ..models import Post
from django.core.exceptions import ValidationError
from django.utils import timezone

class PostService(BaseService):
    def __init__(self):
        super().__init__(PostRepository())
    
    def create_post(self, title, content, author, status='draft'):
        """Create a new post with validation."""
        # Business logic validation
        if len(title.strip()) < 5:
            raise ValidationError("Title must be at least 5 characters long")
        
        if len(content.strip()) < 50:
            raise ValidationError("Content must be at least 50 characters long")
        
        # Create the post
        post = self.repository.create(
            title=title.strip(),
            content=content.strip(),
            author=author,
            status=status,
            created_at=timezone.now()
        )
        
        # Additional business logic
        self._notify_followers(author, post)
        self._update_author_stats(author)
        
        return post
    
    def publish_post(self, post_id, user):
        """Publish a post with authorization checks."""
        post = self.repository.get_by_id(post_id)
        if not post:
            raise ValidationError("Post not found")
        
        # Authorization check
        if post.author != user and not user.is_staff:
            raise ValidationError("You don't have permission to publish this post")
        
        # Business logic
        if post.status == 'published':
            raise ValidationError("Post is already published")
        
        # Update post
        post = self.repository.update(post, status='published', published_at=timezone.now())
        
        # Additional business logic
        self._send_publication_notifications(post)
        self._update_search_index(post)
        
        return post
    
    def get_trending_posts(self, days=7, limit=10):
        """Get trending posts based on views and comments."""
        from django.db.models import Count, F
        
        recent_posts = self.repository.get_recent_posts(days)
        trending_posts = recent_posts.annotate(
            engagement_score=F('view_count') + Count('comments') * 5
        ).order_by('-engagement_score')[:limit]
        
        return trending_posts
    
    def _notify_followers(self, author, post):
        """Notify author's followers about new post."""
        # Implementation for notification logic
        pass
    
    def _update_author_stats(self, author):
        """Update author statistics."""
        # Implementation for updating author stats
        pass
    
    def _send_publication_notifications(self, post):
        """Send notifications when post is published."""
        # Implementation for publication notifications
        pass
    
    def _update_search_index(self, post):
        """Update search index with published post."""
        # Implementation for search index update
        pass
```

### Factory Pattern

#### Model Factory

```python
# factories/post_factory.py
from ..models import Post, Category, Tag
from django.contrib.auth.models import User

class PostFactory:
    """Factory for creating different types of posts."""
    
    @staticmethod
    def create_blog_post(title, content, author, category_name=None, tags=None):
        """Create a standard blog post."""
        post = Post.objects.create(
            title=title,
            content=content,
            author=author,
            post_type='blog',
            status='draft'
        )
        
        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)
            post.category = category
            post.save()
        
        if tags:
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
        
        return post
    
    @staticmethod
    def create_news_article(title, content, author, source=None):
        """Create a news article post."""
        post = Post.objects.create(
            title=title,
            content=content,
            author=author,
            post_type='news',
            status='draft',
            source=source
        )
        
        # Add news-specific metadata
        post.metadata = {
            'article_type': 'news',
            'requires_fact_check': True,
            'priority': 'normal'
        }
        post.save()
        
        return post
    
    @staticmethod
    def create_tutorial(title, content, author, difficulty='beginner', prerequisites=None):
        """Create a tutorial post."""
        post = Post.objects.create(
            title=title,
            content=content,
            author=author,
            post_type='tutorial',
            status='draft'
        )
        
        # Add tutorial-specific metadata
        post.metadata = {
            'difficulty': difficulty,
            'prerequisites': prerequisites or [],
            'estimated_time': None,
            'completion_rate': 0
        }
        post.save()
        
        return post
```

### Observer Pattern with Django Signals

#### Event System Implementation

```python
# events/post_events.py
from django.dispatch import Signal

# Define events
post_viewed = Signal()
post_liked = Signal()
post_shared = Signal()
comment_added = Signal()

# events/handlers.py
from django.dispatch import receiver
from .post_events import post_viewed, post_liked, post_shared, comment_added
from ..models import Post, UserActivity, Notification

@receiver(post_viewed)
def track_post_view(sender, post, user, **kwargs):
    """Track when a post is viewed."""
    # Update view count
    Post.objects.filter(id=post.id).update(view_count=F('view_count') + 1)
    
    # Track user activity
    if user.is_authenticated:
        UserActivity.objects.create(
            user=user,
            action='viewed_post',
            object_id=post.id,
            object_type='post'
        )

@receiver(post_liked)
def handle_post_like(sender, post, user, **kwargs):
    """Handle when a post is liked."""
    # Create notification for post author
    if post.author != user:
        Notification.objects.create(
            user=post.author,
            message=f"{user.username} liked your post '{post.title}'",
            type='like',
            related_object_id=post.id
        )
    
    # Update post popularity score
    post.popularity_score = F('popularity_score') + 1
    post.save(update_fields=['popularity_score'])

@receiver(comment_added)
def handle_new_comment(sender, comment, **kwargs):
    """Handle when a comment is added to a post."""
    post = comment.post
    
    # Notify post author
    if post.author != comment.author:
        Notification.objects.create(
            user=post.author,
            message=f"{comment.author.username} commented on your post '{post.title}'",
            type='comment',
            related_object_id=comment.id
        )
    
    # Update post engagement score
    post.engagement_score = F('engagement_score') + 2
    post.save(update_fields=['engagement_score'])

# Usage in views
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Trigger post viewed event
    post_viewed.send(sender=Post, post=post, user=request.user)
    
    return render(request, 'posts/detail.html', {'post': post})
```

### Strategy Pattern

#### Content Processing Strategy

```python
# strategies/content_processors.py
from abc import ABC, abstractmethod

class ContentProcessor(ABC):
    """Abstract base class for content processors."""
    
    @abstractmethod
    def process(self, content):
        pass

class MarkdownProcessor(ContentProcessor):
    """Process Markdown content."""
    
    def process(self, content):
        import markdown
        return markdown.markdown(content, extensions=['codehilite', 'fenced_code'])

class HTMLProcessor(ContentProcessor):
    """Process HTML content."""
    
    def process(self, content):
        import bleach
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'img']
        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height']
        }
        return bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes)

class PlainTextProcessor(ContentProcessor):
    """Process plain text content."""
    
    def process(self, content):
        import html
        # Escape HTML and convert line breaks
        escaped_content = html.escape(content)
        return escaped_content.replace('\n', '<br>')

# Content processing context
class ContentProcessorContext:
    def __init__(self, processor: ContentProcessor):
        self._processor = processor
    
    def set_processor(self, processor: ContentProcessor):
        self._processor = processor
    
    def process_content(self, content):
        return self._processor.process(content)

# Usage in models
class Post(models.Model):
    title = models.CharField(max_length=200)
    raw_content = models.TextField()
    processed_content = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=[
        ('markdown', 'Markdown'),
        ('html', 'HTML'),
        ('plain', 'Plain Text')
    ], default='markdown')
    
    def save(self, *args, **kwargs):
        # Process content based on type
        processor_map = {
            'markdown': MarkdownProcessor(),
            'html': HTMLProcessor(),
            'plain': PlainTextProcessor()
        }
        
        processor = processor_map.get(self.content_type, PlainTextProcessor())
        context = ContentProcessorContext(processor)
        self.processed_content = context.process_content(self.raw_content)
        
        super().save(*args, **kwargs)
```

### Decorator Pattern

#### View Decorators

```python
# decorators/view_decorators.py
from functools import wraps
from django.http import JsonResponse, HttpResponseForbidden
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
import time

def api_key_required(view_func):
    """Decorator to require API key for view access."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key or not validate_api_key(api_key):
            return JsonResponse({'error': 'Valid API key required'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

def rate_limit(requests_per_minute=60):
    """Decorator to rate limit view access."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            cache_key = f"rate_limit_{client_ip}_{view_func.__name__}"
            
            # Get current request count
            current_requests = cache.get(cache_key, 0)
            
            if current_requests >= requests_per_minute:
                return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
            
            # Increment counter
            cache.set(cache_key, current_requests + 1, 60)  # 60 seconds TTL
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def cache_response(timeout=300):
    """Decorator to cache view responses."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Create cache key from view name and arguments
            cache_key = f"view_cache_{view_func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Try to get cached response
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
            
            # Generate response and cache it
            response = view_func(request, *args, **kwargs)
            cache.set(cache_key, response, timeout)
            
            return response
        return wrapper
    return decorator

def log_execution_time(view_func):
    """Decorator to log view execution time."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        response = view_func(request, *args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.info(f"View {view_func.__name__} executed in {execution_time:.2f}s")
        
        return response
    return wrapper

# Usage
@api_key_required
@rate_limit(requests_per_minute=100)
@cache_response(timeout=600)
@log_execution_time
def api_posts_list(request):
    posts = Post.objects.published().select_related('author')
    data = [{'id': p.id, 'title': p.title, 'author': p.author.username} for p in posts]
    return JsonResponse({'posts': data})
```

### Command Pattern

#### Command Implementation

```python
# commands/base_command.py
from abc import ABC, abstractmethod

class Command(ABC):
    """Abstract base command."""
    
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

# commands/post_commands.py
from .base_command import Command
from ..models import Post
from ..services.post_service import PostService

class CreatePostCommand(Command):
    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author
        self.post = None
        self.service = PostService()
    
    def execute(self):
        self.post = self.service.create_post(
            title=self.title,
            content=self.content,
            author=self.author
        )
        return self.post
    
    def undo(self):
        if self.post:
            self.post.delete()
            self.post = None

class PublishPostCommand(Command):
    def __init__(self, post_id, user):
        self.post_id = post_id
        self.user = user
        self.previous_status = None
        self.service = PostService()
    
    def execute(self):
        post = Post.objects.get(id=self.post_id)
        self.previous_status = post.status
        return self.service.publish_post(self.post_id, self.user)
    
    def undo(self):
        if self.previous_status:
            post = Post.objects.get(id=self.post_id)
            post.status = self.previous_status
            post.save()

# Command invoker
class CommandInvoker:
    def __init__(self):
        self.history = []
    
    def execute_command(self, command):
        result = command.execute()
        self.history.append(command)
        return result
    
    def undo_last_command(self):
        if self.history:
            command = self.history.pop()
            command.undo()
    
    def undo_all_commands(self):
        while self.history:
            self.undo_last_command()

# Usage
def create_and_publish_post(request):
    invoker = CommandInvoker()
    
    try:
        # Create post
        create_command = CreatePostCommand(
            title=request.POST['title'],
            content=request.POST['content'],
            author=request.user
        )
        post = invoker.execute_command(create_command)
        
        # Publish post
        publish_command = PublishPostCommand(post.id, request.user)
        invoker.execute_command(publish_command)
        
        return JsonResponse({'success': True, 'post_id': post.id})
        
    except Exception as e:
        # Undo all commands on error
        invoker.undo_all_commands()
        return JsonResponse({'error': str(e)}, status=400)
```

## Best Practices and Guidelines

### 1. Middleware Best Practices
- Keep middleware lightweight and focused on a single responsibility
- Order middleware carefully in settings.py
- Handle exceptions gracefully to avoid breaking the request/response cycle
- Use caching wisely to avoid performance bottlenecks

### 2. Signal Best Practices
- Import signal handlers in the app's ready() method to avoid circular imports
- Handle exceptions in signal handlers to prevent breaking the main flow
- Be cautious with database operations in signals to avoid infinite loops
- Use signals for decoupled communication, not for core business logic

### 3. ORM Best Practices
- Use select_related() and prefetch_related() to avoid N+1 queries
- Create custom managers and querysets for reusable query logic
- Use database indexes for frequently queried fields
- Consider using raw SQL for complex queries that are difficult to express with the ORM

### 4. Design Pattern Best Practices
- Choose patterns that solve real problems, not just for the sake of using patterns
- Keep patterns simple and focused on their intended purpose
- Document pattern usage and rationale for future maintainers
- Test pattern implementations thoroughly

## Conclusion

Advanced Django patterns help create more maintainable, scalable, and robust applications. By understanding and applying these patterns appropriately, you can build Django applications that are easier to test, extend, and maintain over time.

Remember that patterns are tools to solve specific problems. Always consider the complexity they add versus the benefits they provide, and choose the right pattern for your specific use case.