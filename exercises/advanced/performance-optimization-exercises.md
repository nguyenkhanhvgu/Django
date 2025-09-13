# Django Performance Optimization Exercises

These hands-on exercises will help you practice the performance optimization techniques covered in the advanced tutorial. Each exercise includes a problem scenario, implementation tasks, and verification steps.

## Prerequisites

- Completed intermediate Django tutorials
- Understanding of Django ORM, caching, and testing
- Redis or Memcached installed for caching exercises
- Basic knowledge of SQL and database concepts

## Exercise 1: Query Optimization

### Scenario
You have a blog application with performance issues. The post list page is loading slowly due to inefficient database queries.

### Setup
```python
# models.py
class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField()

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

class Tag(models.Model):
    name = models.CharField(max_length=30)

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### Tasks

#### Task 1.1: Identify N+1 Query Problems
Create a view that demonstrates the N+1 query problem:

```python
# views.py - PROBLEMATIC VERSION
def post_list_bad(request):
    posts = Post.objects.all()[:10]
    for post in posts:
        print(f"Post: {post.title}")
        print(f"Author: {post.author.name}")  # N+1 problem here
        print(f"Category: {post.category.name}")  # N+1 problem here
        print(f"Tags: {[tag.name for tag in post.tags.all()]}")  # N+1 problem here
    return render(request, 'posts/list.html', {'posts': posts})
```

**Your Task**: 
1. Run this view and count the database queries using Django Debug Toolbar
2. Document how many queries are executed
3. Explain why this is inefficient

#### Task 1.2: Optimize with select_related()
Fix the foreign key N+1 problems:

```python
def post_list_optimized_step1(request):
    # TODO: Use select_related() to optimize foreign key access
    posts = Post.objects.all()[:10]  # Modify this line
    
    for post in posts:
        print(f"Post: {post.title}")
        print(f"Author: {post.author.name}")
        print(f"Category: {post.category.name}")
    
    return render(request, 'posts/list.html', {'posts': posts})
```

**Your Task**: 
1. Modify the queryset to use `select_related()`
2. Verify the query count is reduced
3. Measure the performance improvement

#### Task 1.3: Optimize with prefetch_related()
Fix the many-to-many N+1 problem:

```python
def post_list_optimized_step2(request):
    # TODO: Add prefetch_related() for tags
    posts = Post.objects.select_related('author', 'category').all()[:10]
    
    for post in posts:
        print(f"Post: {post.title}")
        print(f"Author: {post.author.name}")
        print(f"Category: {post.category.name}")
        print(f"Tags: {[tag.name for tag in post.tags.all()]}")  # Still N+1 here
    
    return render(request, 'posts/list.html', {'posts': posts})
```

**Your Task**: 
1. Add `prefetch_related()` for tags
2. Verify all N+1 problems are resolved
3. Document the final query count

#### Task 1.4: Advanced Prefetch with Filtering
Optimize comment loading with filtering:

```python
def post_list_with_comments(request):
    # TODO: Use Prefetch to load only approved comments
    from django.db.models import Prefetch
    
    posts = Post.objects.select_related('author', 'category').prefetch_related('tags').all()[:10]
    
    for post in posts:
        comments = post.comments.filter(approved=True)  # This creates N+1
        print(f"Post: {post.title} has {comments.count()} approved comments")
    
    return render(request, 'posts/list_with_comments.html', {'posts': posts})
```

**Your Task**: 
1. Use `Prefetch` to load only approved comments
2. Store prefetched comments in a custom attribute
3. Verify no additional queries are made when accessing comments

### Verification
- [ ] Original view executes 31+ queries (1 + 10*3 for posts, authors, categories, tags)
- [ ] Step 1 optimization reduces queries to 21 (1 query with JOINs + 10 for tags)
- [ ] Step 2 optimization reduces queries to 2 (1 for posts with JOINs + 1 for tags)
- [ ] Advanced prefetch loads comments efficiently

---

## Exercise 2: Caching Implementation

### Scenario
Your blog application needs caching to handle increased traffic. Implement various caching strategies.

### Tasks

#### Task 2.1: Basic View Caching
Implement per-view caching:

```python
# views.py
from django.views.decorators.cache import cache_page

# TODO: Add cache_page decorator
def popular_posts(request):
    # Simulate expensive operation
    time.sleep(1)  # Remove this in real code
    posts = Post.objects.filter(views__gt=100).order_by('-views')[:10]
    return render(request, 'posts/popular.html', {'posts': posts})
```

**Your Task**: 
1. Add `@cache_page(60 * 15)` decorator (15 minutes)
2. Test that subsequent requests are served from cache
3. Verify response time improvement

#### Task 2.2: Template Fragment Caching
Implement template fragment caching:

```html
<!-- templates/posts/list.html -->
<!-- TODO: Add cache template tags around expensive sections -->
{% load cache %}

<div class="sidebar">
    <!-- Cache this expensive sidebar for 30 minutes -->
    <h3>Popular Tags</h3>
    {% for tag in popular_tags %}
        <span class="tag">{{ tag.name }} ({{ tag.post_count }})</span>
    {% endfor %}
</div>

<div class="main-content">
    {% for post in posts %}
        <!-- Cache individual post rendering for 10 minutes -->
        <article>
            <h2>{{ post.title }}</h2>
            <p>By {{ post.author.name }} in {{ post.category.name }}</p>
            <p>{{ post.content|truncatewords:50 }}</p>
        </article>
    {% endfor %}
</div>
```

**Your Task**: 
1. Add `{% cache %}` tags around the sidebar
2. Add `{% cache %}` tags around individual posts
3. Use appropriate cache keys and timeouts

#### Task 2.3: Low-Level Cache API
Implement custom caching logic:

```python
# utils/cache_utils.py
from django.core.cache import cache

def get_user_dashboard_data(user_id):
    cache_key = f'user_dashboard_{user_id}'
    
    # TODO: Implement cache-aside pattern
    data = None  # Try to get from cache first
    
    if data is None:
        # Simulate expensive data gathering
        data = {
            'user_posts': list(Post.objects.filter(author_id=user_id).values('title', 'views')),
            'total_views': Post.objects.filter(author_id=user_id).aggregate(total=models.Sum('views'))['total'] or 0,
            'recent_comments': list(Comment.objects.filter(post__author_id=user_id).order_by('-created_at')[:5].values())
        }
        # TODO: Cache the data
    
    return data

def invalidate_user_cache(user_id):
    # TODO: Implement cache invalidation
    pass
```

**Your Task**: 
1. Implement cache retrieval with `cache.get()`
2. Implement cache storage with `cache.set()`
3. Implement cache invalidation
4. Add appropriate error handling

#### Task 2.4: Redis Advanced Patterns
Implement advanced Redis caching:

```python
# utils/redis_cache.py
from django_redis import get_redis_connection
import json

class AdvancedRedisCache:
    def __init__(self):
        self.redis_conn = get_redis_connection('default')
    
    def set_with_tags(self, key, value, timeout=3600, tags=None):
        # TODO: Implement tagged caching
        pass
    
    def invalidate_by_tag(self, tag):
        # TODO: Implement tag-based invalidation
        pass
    
    def get_or_set_json(self, key, callable_func, timeout=3600):
        # TODO: Implement JSON caching with callable
        pass
```

**Your Task**: 
1. Implement tagged caching system
2. Implement tag-based cache invalidation
3. Implement JSON serialization caching
4. Test all methods work correctly

### Verification
- [ ] View caching reduces response time significantly
- [ ] Template fragments are cached independently
- [ ] Low-level cache API works with proper invalidation
- [ ] Redis advanced patterns function correctly
- [ ] Cache hit rates are measurable and reasonable

---

## Exercise 3: Database Performance Optimization

### Scenario
Your application has database performance issues. Optimize queries and database structure.

### Tasks

#### Task 3.1: Add Database Indexes
Analyze and add appropriate indexes:

```python
# models.py - Add indexes to existing models
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=False)
    
    class Meta:
        # TODO: Add appropriate indexes
        indexes = [
            # Add indexes for common query patterns
        ]
```

**Your Task**: 
1. Identify common query patterns in your views
2. Add composite indexes for frequently filtered combinations
3. Add indexes for ordering fields
4. Create and run migrations

#### Task 3.2: Bulk Operations
Optimize data creation and updates:

```python
# management/commands/create_test_data.py
def create_posts_inefficient(count=1000):
    # TODO: Replace with bulk operations
    for i in range(count):
        Post.objects.create(
            title=f'Post {i}',
            content=f'Content for post {i}',
            author_id=1,
            category_id=1
        )

def update_post_views_inefficient(post_ids):
    # TODO: Replace with bulk update
    for post_id in post_ids:
        post = Post.objects.get(id=post_id)
        post.views += 1
        post.save()
```

**Your Task**: 
1. Replace individual creates with `bulk_create()`
2. Replace individual updates with `bulk_update()` or `update()`
3. Measure performance improvement
4. Handle any limitations of bulk operations

#### Task 3.3: Query Optimization
Optimize complex queries:

```python
# views.py
def author_statistics(request):
    # TODO: Optimize this query
    authors = []
    for author in Author.objects.all():
        author_data = {
            'name': author.name,
            'post_count': author.posts.count(),  # N+1 query
            'total_views': sum(post.views for post in author.posts.all()),  # N+1 query
            'avg_views': author.posts.aggregate(avg=models.Avg('views'))['avg'],  # N+1 query
            'latest_post': author.posts.order_by('-created_at').first()  # N+1 query
        }
        authors.append(author_data)
    
    return render(request, 'authors/statistics.html', {'authors': authors})
```

**Your Task**: 
1. Use `annotate()` to calculate statistics in the database
2. Use `select_related()` for the latest post
3. Reduce to a single query
4. Verify performance improvement

### Verification
- [ ] Appropriate indexes are added and improve query performance
- [ ] Bulk operations significantly reduce execution time
- [ ] Complex queries are optimized to minimal database hits
- [ ] Query execution plans show index usage

---

## Exercise 4: Performance Testing and Monitoring

### Scenario
Set up comprehensive performance testing and monitoring for your application.

### Tasks

#### Task 4.1: Load Testing with Locust
Create comprehensive load tests:

```python
# locustfile.py
from locust import HttpUser, task, between

class BlogUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # TODO: Implement user authentication
        pass
    
    @task(3)
    def view_posts(self):
        # TODO: Test post list view
        pass
    
    @task(1)
    def create_post(self):
        # TODO: Test post creation
        pass
    
    @task(2)
    def search_posts(self):
        # TODO: Test search functionality
        pass
```

**Your Task**: 
1. Implement user authentication in `on_start()`
2. Add realistic task weights and behaviors
3. Include error handling and response validation
4. Test different user scenarios

#### Task 4.2: Performance Monitoring Middleware
Create monitoring middleware:

```python
# middleware/performance.py
import time
from django.db import connection

class PerformanceMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # TODO: Record start metrics
        
        response = self.get_response(request)
        
        # TODO: Calculate and log performance metrics
        
        return response
```

**Your Task**: 
1. Record request start time and query count
2. Calculate response time and query count
3. Log slow requests and high query counts
4. Add performance headers to response

#### Task 4.3: Custom Performance Tests
Write automated performance tests:

```python
# tests/test_performance.py
from django.test import TestCase, TransactionTestCase
from django.db import connection
import time

class PerformanceTestCase(TestCase):
    def setUp(self):
        # TODO: Set up performance monitoring
        pass
    
    def test_post_list_performance(self):
        # TODO: Test post list view performance
        # Assert query count and response time
        pass
    
    def test_bulk_operations_performance(self):
        # TODO: Test bulk operations performance
        pass
```

**Your Task**: 
1. Create base performance test class
2. Test critical view performance
3. Test database operation performance
4. Set performance budgets and assertions

### Verification
- [ ] Load tests run successfully and provide meaningful metrics
- [ ] Monitoring middleware captures performance data
- [ ] Performance tests catch regressions
- [ ] Performance budgets are enforced

---

## Exercise 5: Production Optimization

### Scenario
Prepare your application for production with comprehensive optimizations.

### Tasks

#### Task 5.1: Static File Optimization
Optimize static file handling:

```python
# settings/production.py
# TODO: Configure static file optimization
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# TODO: Add compression settings
COMPRESS_ENABLED = False
```

**Your Task**: 
1. Configure `ManifestStaticFilesStorage`
2. Set up compression with `django-compressor`
3. Configure CDN settings
4. Optimize image handling

#### Task 5.2: Database Connection Optimization
Optimize database connections:

```python
# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'blog_db',
        'USER': 'blog_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        # TODO: Add connection optimization settings
    }
}
```

**Your Task**: 
1. Configure connection pooling
2. Set appropriate connection limits
3. Configure read/write database splitting
4. Add connection monitoring

#### Task 5.3: Caching Strategy
Implement production caching:

```python
# settings/production.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            # TODO: Add production Redis settings
        }
    }
}
```

**Your Task**: 
1. Configure Redis with appropriate settings
2. Set up cache key versioning
3. Configure cache timeouts
4. Implement cache warming strategy

### Verification
- [ ] Static files are optimized and compressed
- [ ] Database connections are properly pooled
- [ ] Caching is configured for production load
- [ ] All optimizations work together effectively

---

## Bonus Challenges

### Challenge 1: Custom Cache Backend
Create a custom cache backend that combines Redis and local memory caching.

### Challenge 2: Query Optimization Tool
Build a Django management command that analyzes your application's queries and suggests optimizations.

### Challenge 3: Real-time Performance Dashboard
Create a real-time dashboard showing application performance metrics using WebSockets.

### Challenge 4: Automated Performance Testing
Set up CI/CD pipeline that runs performance tests and fails builds that don't meet performance budgets.

---

## Solutions and Discussion

After completing the exercises, compare your solutions with the provided examples in the `code-examples/performance-optimization/` directory. Consider:

1. **Query Optimization**: How much did you reduce query counts? What was the performance impact?

2. **Caching Strategy**: What cache hit rates did you achieve? How did different caching strategies compare?

3. **Load Testing**: What bottlenecks did you discover? How did your application perform under load?

4. **Monitoring**: What insights did your monitoring provide? What would you optimize next?

5. **Production Readiness**: How confident are you that your optimizations will work in production?

## Next Steps

After completing these exercises:

1. Apply these techniques to your own Django projects
2. Set up monitoring in your production environment
3. Regularly review and optimize performance
4. Stay updated with Django performance best practices
5. Consider advanced topics like database sharding and microservices

Remember: Performance optimization is an ongoing process. Always measure before optimizing, and focus on the bottlenecks that have the biggest impact on user experience.