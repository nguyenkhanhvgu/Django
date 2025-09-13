"""
Django Query Optimization Examples

This module demonstrates various query optimization techniques
including select_related, prefetch_related, and bulk operations.
"""

from django.db import models, connection
from django.utils import timezone
import time


# Sample Models for Demonstration
class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    views = models.PositiveIntegerField(default=0)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['published', 'created_at']),
            models.Index(fields=['author', 'published']),
            models.Index(fields=['category', 'published']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['post', 'approved']),
        ]


# Query Optimization Examples

def demonstrate_n_plus_one_problem():
    """Demonstrate the N+1 query problem and its solution"""
    print("=== N+1 Query Problem Demonstration ===")
    
    # BAD: N+1 queries
    print("\n1. BAD: N+1 queries")
    start_queries = len(connection.queries)
    start_time = time.time()
    
    posts = Post.objects.filter(published=True)[:10]
    for post in posts:
        print(f"Post: {post.title} by {post.author.name}")  # Each iteration hits DB
    
    end_time = time.time()
    end_queries = len(connection.queries)
    print(f"Queries executed: {end_queries - start_queries}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    
    # GOOD: Single query with JOIN
    print("\n2. GOOD: Single query with JOIN")
    start_queries = len(connection.queries)
    start_time = time.time()
    
    posts = Post.objects.select_related('author').filter(published=True)[:10]
    for post in posts:
        print(f"Post: {post.title} by {post.author.name}")  # No additional DB hits
    
    end_time = time.time()
    end_queries = len(connection.queries)
    print(f"Queries executed: {end_queries - start_queries}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")


def demonstrate_select_related():
    """Demonstrate select_related for foreign key optimization"""
    print("\n=== select_related() Demonstration ===")
    
    # Multiple foreign keys
    posts = Post.objects.select_related('author', 'category').filter(published=True)[:5]
    
    print("Posts with authors and categories (single query):")
    for post in posts:
        print(f"'{post.title}' by {post.author.name} in {post.category.name}")


def demonstrate_prefetch_related():
    """Demonstrate prefetch_related for many-to-many and reverse FK optimization"""
    print("\n=== prefetch_related() Demonstration ===")
    
    # BAD: Multiple queries for tags
    print("\n1. BAD: Multiple queries for tags")
    start_queries = len(connection.queries)
    
    posts = Post.objects.filter(published=True)[:5]
    for post in posts:
        tags = list(post.tags.all())  # Separate query for each post
        print(f"Post: {post.title}, Tags: {[tag.name for tag in tags]}")
    
    end_queries = len(connection.queries)
    print(f"Queries executed: {end_queries - start_queries}")
    
    # GOOD: Prefetch related objects
    print("\n2. GOOD: Prefetch related objects")
    start_queries = len(connection.queries)
    
    posts = Post.objects.prefetch_related('tags').filter(published=True)[:5]
    for post in posts:
        tags = list(post.tags.all())  # Uses prefetched data
        print(f"Post: {post.title}, Tags: {[tag.name for tag in tags]}")
    
    end_queries = len(connection.queries)
    print(f"Queries executed: {end_queries - start_queries}")


def demonstrate_prefetch_related_advanced():
    """Demonstrate advanced prefetch_related usage"""
    from django.db.models import Prefetch
    
    print("\n=== Advanced prefetch_related() ===")
    
    # Prefetch with filtering
    approved_comments = Prefetch(
        'comments',
        queryset=Comment.objects.filter(approved=True).select_related('post'),
        to_attr='approved_comments'
    )
    
    posts = Post.objects.prefetch_related(approved_comments).filter(published=True)[:3]
    
    for post in posts:
        print(f"Post: {post.title}")
        print(f"Approved comments: {len(post.approved_comments)}")
        for comment in post.approved_comments:
            print(f"  - {comment.author_name}: {comment.content[:50]}...")


def demonstrate_only_and_defer():
    """Demonstrate only() and defer() for field selection"""
    print("\n=== only() and defer() Demonstration ===")
    
    # Only fetch specific fields
    print("\n1. Using only() - fetch only specific fields")
    posts = Post.objects.only('title', 'created_at', 'author__name').select_related('author')[:5]
    
    for post in posts:
        print(f"Title: {post.title}, Author: {post.author.name}, Created: {post.created_at}")
        # Accessing 'content' would trigger another query
    
    # Defer large fields
    print("\n2. Using defer() - defer large fields")
    posts = Post.objects.defer('content').filter(published=True)[:5]
    
    for post in posts:
        print(f"Title: {post.title}, Views: {post.views}")
        # 'content' is not loaded unless accessed


def demonstrate_bulk_operations():
    """Demonstrate bulk operations for better performance"""
    print("\n=== Bulk Operations Demonstration ===")
    
    # Bulk create
    print("\n1. Bulk create example")
    start_time = time.time()
    
    # Create sample data
    bulk_posts = []
    author = Author.objects.first()
    category = Category.objects.first()
    
    for i in range(100):
        bulk_posts.append(Post(
            title=f'Bulk Post {i}',
            slug=f'bulk-post-{i}',
            content=f'Content for bulk post {i}',
            author=author,
            category=category,
            published=True
        ))
    
    Post.objects.bulk_create(bulk_posts, batch_size=50)
    
    end_time = time.time()
    print(f"Created 100 posts in {end_time - start_time:.4f} seconds")
    
    # Bulk update
    print("\n2. Bulk update example")
    start_time = time.time()
    
    Post.objects.filter(title__startswith='Bulk Post').update(views=100)
    
    end_time = time.time()
    print(f"Updated posts in {end_time - start_time:.4f} seconds")


def demonstrate_query_optimization_techniques():
    """Demonstrate various query optimization techniques"""
    print("\n=== Query Optimization Techniques ===")
    
    # 1. Use exists() instead of len() or count()
    print("\n1. Using exists() for boolean checks")
    
    # BAD
    if Post.objects.filter(author__name='John Doe').count() > 0:
        print("John Doe has posts (using count)")
    
    # GOOD
    if Post.objects.filter(author__name='John Doe').exists():
        print("John Doe has posts (using exists)")
    
    # 2. Use iterator() for large datasets
    print("\n2. Using iterator() for large datasets")
    
    # Process large datasets without loading all into memory
    for post in Post.objects.filter(published=True).iterator(chunk_size=100):
        # Process each post without loading all posts into memory
        pass
    print("Processed posts using iterator")
    
    # 3. Use values() and values_list() for specific data
    print("\n3. Using values() for specific data")
    
    # Get only specific fields as dictionaries
    post_data = Post.objects.values('title', 'author__name', 'created_at')[:5]
    for data in post_data:
        print(f"Title: {data['title']}, Author: {data['author__name']}")
    
    # Get specific fields as tuples
    post_titles = Post.objects.values_list('title', flat=True)[:5]
    print(f"Post titles: {list(post_titles)}")


def demonstrate_database_functions():
    """Demonstrate database functions for optimization"""
    from django.db.models import Count, Avg, Max, Min, F, Q
    from django.db.models.functions import Lower, Upper, Concat
    
    print("\n=== Database Functions Demonstration ===")
    
    # Aggregation
    stats = Post.objects.aggregate(
        total_posts=Count('id'),
        avg_views=Avg('views'),
        max_views=Max('views'),
        min_views=Min('views')
    )
    print(f"Post statistics: {stats}")
    
    # Annotation
    authors_with_post_count = Author.objects.annotate(
        post_count=Count('posts')
    ).filter(post_count__gt=0)
    
    for author in authors_with_post_count:
        print(f"{author.name}: {author.post_count} posts")
    
    # F expressions for database-level operations
    Post.objects.filter(id__in=[1, 2, 3]).update(views=F('views') + 1)
    print("Updated post views using F expression")
    
    # Complex queries with Q objects
    complex_posts = Post.objects.filter(
        Q(title__icontains='django') | Q(content__icontains='python'),
        published=True
    ).select_related('author')
    
    print(f"Found {complex_posts.count()} posts matching complex criteria")


def demonstrate_custom_managers():
    """Demonstrate custom managers for query optimization"""
    
    class OptimizedPostManager(models.Manager):
        def published_with_author(self):
            return self.select_related('author').filter(published=True)
        
        def with_comment_count(self):
            return self.annotate(comment_count=Count('comments'))
        
        def popular_posts(self, min_views=100):
            return self.filter(views__gte=min_views).order_by('-views')
    
    # This would be added to the Post model:
    # objects = OptimizedPostManager()
    
    print("\n=== Custom Manager Example ===")
    print("Custom managers provide optimized querysets for common operations")
    print("Example methods:")
    print("- published_with_author(): select_related + filter")
    print("- with_comment_count(): annotate with comment count")
    print("- popular_posts(): filter and order by views")


def run_all_demonstrations():
    """Run all query optimization demonstrations"""
    print("Django Query Optimization Examples")
    print("=" * 50)
    
    try:
        demonstrate_n_plus_one_problem()
        demonstrate_select_related()
        demonstrate_prefetch_related()
        demonstrate_prefetch_related_advanced()
        demonstrate_only_and_defer()
        demonstrate_bulk_operations()
        demonstrate_query_optimization_techniques()
        demonstrate_database_functions()
        demonstrate_custom_managers()
        
        print("\n" + "=" * 50)
        print("All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        print("Make sure you have sample data in your database")


if __name__ == "__main__":
    # This would be run in Django shell
    print("Run this in Django shell with: python manage.py shell")
    print(">>> from database_optimization.query_optimization import *")
    print(">>> run_all_demonstrations()")