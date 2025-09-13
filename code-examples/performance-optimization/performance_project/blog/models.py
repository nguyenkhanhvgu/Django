"""
Blog models with performance optimization examples.
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Author(models.Model):
    """Author model with optimized fields and indexes."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add index for common queries
    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.user.username
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


class Category(models.Model):
    """Category model with slug for SEO and performance."""
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Tag model for post categorization."""
    name = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PostQuerySet(models.QuerySet):
    """Custom QuerySet with performance optimizations."""
    
    def published(self):
        """Filter published posts."""
        return self.filter(status='published', published_at__lte=timezone.now())
    
    def with_author(self):
        """Select related author data to avoid N+1 queries."""
        return self.select_related('author__user')
    
    def with_categories(self):
        """Prefetch categories to avoid N+1 queries."""
        return self.prefetch_related('categories')
    
    def with_tags(self):
        """Prefetch tags to avoid N+1 queries."""
        return self.prefetch_related('tags')
    
    def optimized(self):
        """Apply all common optimizations."""
        return self.with_author().with_categories().with_tags()
    
    def recent(self, limit=10):
        """Get recent posts with limit."""
        return self.published().order_by('-published_at')[:limit]


class PostManager(models.Manager):
    """Custom manager for Post model."""
    
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def optimized(self):
        return self.get_queryset().optimized()
    
    def recent(self, limit=10):
        return self.get_queryset().recent(limit)


class Post(models.Model):
    """Post model with performance optimizations."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True, help_text="Short description for listings")
    
    # Use select_related for these foreign keys
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    featured = models.BooleanField(default=False, db_index=True)
    
    # Timestamps with indexes for common queries
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    # SEO and performance fields
    meta_description = models.CharField(max_length=160, blank=True)
    view_count = models.PositiveIntegerField(default=0, db_index=True)
    
    # Custom manager
    objects = PostManager()
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        # Composite indexes for common query patterns
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['featured', 'published_at']),
            models.Index(fields=['status', 'featured', 'published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        """Override save to set published_at when status changes to published."""
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        """Check if post is published and publication date has passed."""
        return (
            self.status == 'published' and 
            self.published_at and 
            self.published_at <= timezone.now()
        )


class Comment(models.Model):
    """Comment model with performance considerations."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'is_approved', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"


class PostView(models.Model):
    """Track post views for analytics (optimized for high-volume inserts)."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_views')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        # Partition by date for better performance
        indexes = [
            models.Index(fields=['post', 'viewed_at']),
            models.Index(fields=['viewed_at']),  # For cleanup tasks
        ]
        # Prevent duplicate views from same IP within short timeframe
        unique_together = ['post', 'ip_address', 'viewed_at']