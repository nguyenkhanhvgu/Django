"""
Blog models demonstrating Django relationships and ORM techniques.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models import Count, Avg
from .managers import PublishedPostManager, PublishedPostQuerySet


class UserProfile(models.Model):
    """One-to-One relationship with User model."""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()


class Category(models.Model):
    """Hierarchical categories with self-referencing ForeignKey."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})
    
    @property
    def post_count(self):
        return self.posts.filter(status='published').count()


class Tag(models.Model):
    """Tags for Many-to-Many relationship with Posts."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'slug': self.slug})
    
    @property
    def post_count(self):
        return self.posts.filter(status='published').count()


class Post(models.Model):
    """Main Post model with various relationships."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    
    # Relationships
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    # Status and metadata
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Managers
    objects = models.Manager()
    published = PublishedPostManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.title    
    
def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt:
            self.excerpt = self.content[:297] + '...' if len(self.content) > 300 else self.content
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    @property
    def comment_count(self):
        return self.comments.filter(approved=True).count()
    
    @property
    def content_length(self):
        return len(self.content)


class Comment(models.Model):
    """Comments with ForeignKey to Post."""
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    content = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'approved']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'


# Example of through model for Many-to-Many with additional fields
class Author(models.Model):
    """Author model for demonstrating through relationships."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """Book model with Many-to-Many through relationship."""
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()
    authors = models.ManyToManyField(Author, through='BookAuthor')
    
    def __str__(self):
        return self.title


class BookAuthor(models.Model):
    """Through model for Book-Author relationship with additional fields."""
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # e.g., "Lead Author", "Co-Author"
    order = models.PositiveIntegerField()  # Author order on book cover
    
    class Meta:
        unique_together = ('book', 'author')
        ordering = ['order']
    
    def __str__(self):
        return f'{self.author.name} - {self.book.title} ({self.role})'


# Model for demonstrating database views and complex queries
class PostStatistics(models.Model):
    """Unmanaged model representing a database view."""
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    post_count = models.IntegerField()
    avg_content_length = models.FloatField()
    total_views = models.IntegerField()
    latest_post_date = models.DateTimeField()
    
    class Meta:
        managed = False  # Django won't manage this table
        db_table = 'post_statistics_view'