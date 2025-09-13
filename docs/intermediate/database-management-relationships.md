# Database Management and Relationships in Django

## Table of Contents
1. [Introduction to Django ORM](#introduction)
2. [Model Relationships](#model-relationships)
3. [Database Migrations](#database-migrations)
4. [Query Optimization](#query-optimization)
5. [Advanced ORM Techniques](#advanced-orm)
6. [Complex Database Operations](#complex-operations)
7. [Exercises](#exercises)

## Introduction to Django ORM {#introduction}

Django's Object-Relational Mapping (ORM) provides a powerful abstraction layer between your Python code and the database. This tutorial covers advanced database management techniques, model relationships, and query optimization strategies.

### What You'll Learn
- Master Django model relationships (One-to-One, One-to-Many, Many-to-Many)
- Understand and manage database migrations effectively
- Optimize database queries for better performance
- Use advanced ORM features like aggregation and annotation
- Handle complex database operations and transactions

### Prerequisites
- Completed Django basics tutorial
- Understanding of basic Django models
- Basic SQL knowledge (helpful but not required)

## Model Relationships {#model-relationships}

Django supports three types of relationships between models, each serving different use cases.

### One-to-Many Relationships (ForeignKey)

The most common relationship type, where one record can be related to multiple records in another table.

```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
```

#### Working with ForeignKey Relationships

```python
# Creating related objects
category = Category.objects.create(name="Technology")
user = User.objects.get(username="john")

post = Post.objects.create(
    title="Django Tutorial",
    content="Learning Django ORM...",
    author=user,
    category=category
)

# Accessing related objects
print(post.author.username)  # Forward relationship
print(post.category.name)

# Reverse relationship (using related_name)
user_posts = user.posts.all()  # All posts by this user
category_posts = category.posts.all()  # All posts in this category
```

### One-to-One Relationships (OneToOneField)

Used when you need to extend a model or create a profile-like relationship.

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

# Using signals to automatically create profiles
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```

#### Working with One-to-One Relationships

```python
# Accessing the profile
user = User.objects.get(username="john")
profile = user.profile  # Forward relationship
user_from_profile = profile.user  # Reverse relationship

# Creating with related object
user = User.objects.create_user(username="jane", email="jane@example.com")
profile = UserProfile.objects.create(
    user=user,
    bio="Django developer",
    location="New York"
)
```

### Many-to-Many Relationships (ManyToManyField)

Used when multiple records in one table can be related to multiple records in another table.

```python
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
```

#### Working with Many-to-Many Relationships

```python
# Creating and adding tags
post = Post.objects.create(title="Django ORM", content="...", author=user)
tag1 = Tag.objects.create(name="Django", slug="django")
tag2 = Tag.objects.create(name="Python", slug="python")

# Adding tags to post
post.tags.add(tag1, tag2)

# Or add by ID
post.tags.add(1, 2)

# Remove tags
post.tags.remove(tag1)

# Clear all tags
post.tags.clear()

# Get all posts with a specific tag
django_posts = tag1.posts.all()

# Get all tags for a post
post_tags = post.tags.all()
```

### Through Models for Many-to-Many Relationships

When you need to store additional information about the relationship:

```python
class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13)
    authors = models.ManyToManyField(Author, through='BookAuthor')
    
    def __str__(self):
        return self.title

class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)  # e.g., "Lead Author", "Co-Author"
    order = models.PositiveIntegerField()  # Author order on book cover
    
    class Meta:
        unique_together = ('book', 'author')
        ordering = ['order']
```

#### Working with Through Models

```python
# Creating relationships with additional data
book = Book.objects.create(title="Django Mastery", isbn="1234567890123")
author = Author.objects.create(name="John Doe", email="john@example.com")

BookAuthor.objects.create(
    book=book,
    author=author,
    role="Lead Author",
    order=1
)

# Querying through relationships
book_authors = BookAuthor.objects.filter(book=book).select_related('author')
for ba in book_authors:
    print(f"{ba.author.name} - {ba.role}")
```

## Database Migrations {#database-migrations}

Django migrations are a way of propagating changes you make to your models into your database schema.

### Creating Migrations

```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migration for specific app
python manage.py makemigrations blog

# Create empty migration for custom operations
python manage.py makemigrations --empty blog
```

### Applying Migrations

```bash
# Apply all pending migrations
python manage.py migrate

# Apply migrations for specific app
python manage.py migrate blog

# Apply specific migration
python manage.py migrate blog 0001
```

### Migration Best Practices

#### 1. Data Migrations

```python
# migrations/0002_populate_categories.py
from django.db import migrations

def populate_categories(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    categories = [
        'Technology',
        'Science',
        'Programming',
        'Web Development'
    ]
    
    for category_name in categories:
        Category.objects.get_or_create(name=category_name)

def reverse_populate_categories(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    Category.objects.filter(
        name__in=['Technology', 'Science', 'Programming', 'Web Development']
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(
            populate_categories,
            reverse_populate_categories
        ),
    ]
```

#### 2. Schema Migrations with Data Preservation

```python
# When adding non-nullable field to existing model
class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0002_populate_categories'),
    ]
    
    operations = [
        # First, add the field as nullable
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.SlugField(null=True),
        ),
        # Then populate the field
        migrations.RunPython(
            populate_slugs,
            migrations.RunPython.noop
        ),
        # Finally, make it non-nullable
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
```

### Migration Commands and Troubleshooting

```bash
# Show migration status
python manage.py showmigrations

# Show SQL for migration
python manage.py sqlmigrate blog 0001

# Fake apply migration (mark as applied without running)
python manage.py migrate blog 0001 --fake

# Reverse migration
python manage.py migrate blog 0001

# Reset all migrations for an app
python manage.py migrate blog zero
```

## Query Optimization {#query-optimization}

Efficient database queries are crucial for application performance.

### N+1 Query Problem and Solutions

#### The Problem
```python
# This creates N+1 queries (1 for posts, N for each author)
posts = Post.objects.all()
for post in posts:
    print(post.author.username)  # Database hit for each post
```

#### Solution 1: select_related() for ForeignKey and OneToOne
```python
# This creates only 1 query with JOIN
posts = Post.objects.select_related('author', 'category').all()
for post in posts:
    print(post.author.username)  # No additional database hit
    print(post.category.name)
```

#### Solution 2: prefetch_related() for ManyToMany and reverse ForeignKey
```python
# Efficient loading of many-to-many relationships
posts = Post.objects.prefetch_related('tags').all()
for post in posts:
    for tag in post.tags.all():  # No additional queries
        print(tag.name)

# Efficient loading of reverse foreign key relationships
categories = Category.objects.prefetch_related('posts').all()
for category in categories:
    for post in category.posts.all():  # No additional queries
        print(post.title)
```

### Advanced Prefetching

```python
from django.db.models import Prefetch

# Custom prefetch with filtering
posts = Post.objects.prefetch_related(
    Prefetch(
        'tags',
        queryset=Tag.objects.filter(name__startswith='Django')
    )
).all()

# Nested prefetching
posts = Post.objects.prefetch_related(
    'tags',
    'author__profile'  # Prefetch author and their profile
).all()
```

### Database Functions and Aggregation

```python
from django.db.models import Count, Avg, Sum, Max, Min, F, Q
from django.db.models.functions import Lower, Upper, Concat

# Aggregation
stats = Post.objects.aggregate(
    total_posts=Count('id'),
    avg_content_length=Avg('content__length'),
    latest_post=Max('created_at')
)

# Annotation
posts_with_tag_count = Post.objects.annotate(
    tag_count=Count('tags')
).filter(tag_count__gt=2)

# F expressions for database-level operations
Post.objects.filter(created_at__gt=F('updated_at'))

# Database functions
authors_lower = Author.objects.annotate(
    name_lower=Lower('name')
).values('name_lower')

# Complex annotations
posts_with_author_info = Post.objects.annotate(
    author_full_name=Concat('author__first_name', 'author__last_name')
).values('title', 'author_full_name')
```

### Query Optimization Techniques

#### 1. Use only() and defer()
```python
# Load only specific fields
posts = Post.objects.only('title', 'created_at').all()

# Defer loading of large fields
posts = Post.objects.defer('content').all()
```

#### 2. Use values() and values_list()
```python
# Get dictionaries instead of model instances
post_data = Post.objects.values('title', 'author__username')

# Get tuples
post_titles = Post.objects.values_list('title', flat=True)

# Get specific field pairs
author_posts = Post.objects.values_list('author__username', 'title')
```

#### 3. Bulk Operations
```python
# Bulk create
posts = [
    Post(title=f"Post {i}", content=f"Content {i}", author=user)
    for i in range(100)
]
Post.objects.bulk_create(posts)

# Bulk update
Post.objects.filter(author=user).bulk_update(
    [Post(id=1, title="Updated Title")],
    ['title']
)

# Bulk delete
Post.objects.filter(created_at__lt=old_date).delete()
```

## Advanced ORM Techniques {#advanced-orm}

### Custom Managers and QuerySets

```python
class PublishedPostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status='published')
    
    def by_author(self, author):
        return self.filter(author=author)
    
    def recent(self, days=7):
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)

class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return PublishedPostQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def recent_published(self, days=7):
        return self.get_queryset().published().recent(days)

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = models.Manager()  # Default manager
    published_objects = PublishedPostManager()  # Custom manager
    
    def __str__(self):
        return self.title
```

#### Using Custom Managers
```python
# Using custom manager methods
recent_posts = Post.published_objects.recent_published(days=30)

# Chaining custom queryset methods
popular_tech_posts = Post.objects.published().by_author(tech_author).recent(14)
```

### Raw SQL and Database Functions

```python
# Raw SQL queries
posts = Post.objects.raw(
    "SELECT * FROM blog_post WHERE title ILIKE %s",
    ['%django%']
)

# Execute raw SQL
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute(
        "SELECT author_id, COUNT(*) FROM blog_post GROUP BY author_id"
    )
    results = cursor.fetchall()

# Database functions
from django.db.models.functions import Extract, TruncDate

posts_by_month = Post.objects.annotate(
    month=Extract('created_at', 'month'),
    year=Extract('created_at', 'year')
).values('year', 'month').annotate(
    post_count=Count('id')
).order_by('year', 'month')
```

## Complex Database Operations {#complex-operations}

### Database Transactions

```python
from django.db import transaction

# Atomic decorator
@transaction.atomic
def create_post_with_tags(title, content, author, tag_names):
    post = Post.objects.create(
        title=title,
        content=content,
        author=author
    )
    
    for tag_name in tag_names:
        tag, created = Tag.objects.get_or_create(name=tag_name)
        post.tags.add(tag)
    
    return post

# Atomic context manager
def transfer_posts(from_author, to_author):
    try:
        with transaction.atomic():
            posts = Post.objects.filter(author=from_author)
            posts.update(author=to_author)
            
            # Update author statistics
            from_author.post_count = from_author.posts.count()
            to_author.post_count = to_author.posts.count()
            
            from_author.save()
            to_author.save()
    except Exception as e:
        # Transaction will be rolled back automatically
        print(f"Transfer failed: {e}")

# Savepoints for nested transactions
def complex_operation():
    with transaction.atomic():
        # Outer transaction
        post = Post.objects.create(title="Test", content="Test", author=user)
        
        try:
            with transaction.atomic():
                # Inner transaction (savepoint)
                risky_operation()
        except Exception:
            # Only inner transaction is rolled back
            pass
        
        # Outer transaction continues
        post.save()
```

### Database Constraints and Indexes

```python
class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)  # Unique constraint
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Index
    
    class Meta:
        # Composite unique constraint
        unique_together = [['author', 'slug']]
        
        # Database indexes
        indexes = [
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['title'], name='post_title_idx'),
        ]
        
        # Check constraints (Django 2.2+)
        constraints = [
            models.CheckConstraint(
                check=models.Q(title__length__gt=0),
                name='title_not_empty'
            ),
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]
```

### Database Views and Custom SQL

```python
# Custom database view
class PostStatistics(models.Model):
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    post_count = models.IntegerField()
    avg_content_length = models.FloatField()
    latest_post_date = models.DateTimeField()
    
    class Meta:
        managed = False  # Django won't manage this table
        db_table = 'post_statistics_view'

# Migration to create the view
class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL(
            """
            CREATE VIEW post_statistics_view AS
            SELECT 
                ROW_NUMBER() OVER () as id,
                author_id,
                COUNT(*) as post_count,
                AVG(LENGTH(content)) as avg_content_length,
                MAX(created_at) as latest_post_date
            FROM blog_post
            GROUP BY author_id;
            """,
            reverse_sql="DROP VIEW post_statistics_view;"
        )
    ]
```

## Exercises {#exercises}

### Exercise 1: Blog with Categories and Tags
Create a blog system with the following requirements:
- Posts belong to categories (one-to-many)
- Posts can have multiple tags (many-to-many)
- Authors can have profiles (one-to-one)
- Implement efficient queries to display posts with their categories, tags, and author information

### Exercise 2: E-commerce Product Relationships
Design models for an e-commerce system:
- Products belong to categories
- Products have variants (size, color) with different prices
- Customers can review products
- Orders contain multiple products
- Implement queries to find popular products and customer purchase history

### Exercise 3: Social Media Platform
Create models for a social media platform:
- Users can follow other users (many-to-many self-relationship)
- Users can create posts
- Posts can be liked and commented on
- Implement efficient queries for user feeds and activity streams

### Exercise 4: Query Optimization Challenge
Given a blog with 10,000 posts, 1,000 authors, and 500 tags:
- Write queries to find the most popular tags
- Find authors with the most posts in the last month
- Display recent posts with author and tag information efficiently
- Measure and optimize query performance

### Exercise 5: Advanced Database Operations
Implement the following features:
- Bulk import posts from CSV file
- Archive old posts using database transactions
- Create database views for reporting
- Implement soft delete functionality

## Next Steps

After completing this tutorial, you should:
- Understand Django's relationship types and when to use each
- Be able to write efficient database queries
- Know how to use migrations effectively
- Understand advanced ORM features and optimization techniques

Continue with the Django REST Framework tutorial to learn how to expose your data through APIs, or explore the deployment tutorial to learn how to take your applications to production.