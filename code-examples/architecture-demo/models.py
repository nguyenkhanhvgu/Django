# Django Architecture Demo - Models
# This file demonstrates Django models and their relationships

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    """Blog category model demonstrating basic model structure"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, help_text="Optional category description")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

class Tag(models.Model):
    """Tag model for many-to-many relationship demonstration"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Post(models.Model):
    """Blog post model demonstrating various field types and relationships"""
    
    # Status choices
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=200, help_text="Post title")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly version of title")
    content = models.TextField(help_text="Main post content")
    excerpt = models.TextField(max_length=300, blank=True, help_text="Short description")
    
    # Relationship fields
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    # Status and metadata
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False, help_text="Feature this post on homepage")
    view_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})
    
    @property
    def word_count(self):
        """Calculate approximate word count"""
        return len(self.content.split())
    
    @property
    def reading_time(self):
        """Estimate reading time in minutes (assuming 200 words per minute)"""
        return max(1, self.word_count // 200)
    
    def is_published(self):
        """Check if post is published"""
        return self.status == 'published'
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['slug']),
        ]

class Comment(models.Model):
    """Comment model demonstrating nested relationships"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    # Self-referencing foreign key for nested comments
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'
    
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None
    
    class Meta:
        ordering = ['created_at']

# Example of a model with custom manager
class PublishedPostManager(models.Manager):
    """Custom manager to get only published posts"""
    def get_queryset(self):
        return super().get_queryset().filter(status='published')

# Add the custom manager to Post model (this would be added to the Post class above)
# Post.add_to_class('published', PublishedPostManager())