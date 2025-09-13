# Database Management and Relationships Exercises

## Exercise 1: Blog System with Relationships

### Objective
Create a comprehensive blog system that demonstrates all three types of Django model relationships.

### Requirements
1. Create models for:
   - `Category` (for organizing posts)
   - `Post` (main content)
   - `Tag` (for labeling posts)
   - `UserProfile` (extending User model)
   - `Comment` (for post comments)

2. Implement the following relationships:
   - Posts belong to one category (ForeignKey)
   - Posts can have multiple tags (ManyToManyField)
   - Users have one profile (OneToOneField)
   - Posts can have multiple comments (ForeignKey)

### Starter Code

```python
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "categories"
    
    def __str__(self):
        return self.name

# TODO: Complete the remaining models
class UserProfile(models.Model):
    # Add fields and relationships
    pass

class Tag(models.Model):
    # Add fields
    pass

class Post(models.Model):
    # Add fields and relationships
    pass

class Comment(models.Model):
    # Add fields and relationships
    pass
```

### Tasks
1. Complete all model definitions with appropriate fields and relationships
2. Create and run migrations
3. Create sample data using Django shell
4. Write queries to:
   - Get all posts in a category with their tags
   - Find the most popular tags (used in most posts)
   - Get all comments for posts by a specific author
   - Find users who haven't created any posts

### Solution Validation
Your solution should:
- Use all three relationship types correctly
- Include proper `related_name` attributes
- Have appropriate `on_delete` behaviors
- Include `__str__` methods for all models

---

## Exercise 2: E-commerce Product System

### Objective
Design and implement a product catalog system with complex relationships.

### Requirements
1. Products belong to categories (hierarchical categories supported)
2. Products have variants (different sizes, colors, prices)
3. Customers can review products
4. Track inventory for each product variant
5. Orders contain multiple product variants

### Model Structure
```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    # Add more fields

class Product(models.Model):
    name = models.CharField(max_length=200)
    # Add category relationship and other fields

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Add size, color, price, inventory fields

class Review(models.Model):
    # Add product, customer, rating, comment fields
    pass

class Order(models.Model):
    # Add customer, date, status fields
    pass

class OrderItem(models.Model):
    # Add order, product_variant, quantity, price fields
    pass
```

### Tasks
1. Complete all model definitions
2. Implement methods to:
   - Calculate average product rating
   - Check product variant availability
   - Calculate order total
3. Write queries to:
   - Find best-selling products
   - Get customer purchase history
   - Find products with low inventory
   - Calculate category sales statistics

---

## Exercise 3: Query Optimization Challenge

### Objective
Practice identifying and solving N+1 query problems and other performance issues.

### Scenario
You have a blog with:
- 10,000 posts
- 1,000 authors
- 500 tags
- 50,000 comments

### Problematic Code
```python
# views.py - SLOW implementation
def post_list_slow(request):
    posts = Post.objects.all()[:20]
    
    context = {
        'posts': []
    }
    
    for post in posts:
        post_data = {
            'title': post.title,
            'author_name': post.author.username,  # N+1 query
            'category_name': post.category.name,  # N+1 query
            'tag_count': post.tags.count(),       # N+1 query
            'comment_count': post.comments.count(), # N+1 query
        }
        context['posts'].append(post_data)
    
    return render(request, 'blog/post_list.html', context)
```

### Tasks
1. Identify all performance problems in the code above
2. Rewrite the view to eliminate N+1 queries
3. Use Django Debug Toolbar to measure query count before and after
4. Write optimized queries for:
   - Posts with author, category, and tag information
   - Most commented posts in the last month
   - Authors with their post count and latest post date
   - Tags with their usage count

### Optimization Techniques to Use
- `select_related()`
- `prefetch_related()`
- `annotate()` with `Count()`, `Max()`, etc.
- `only()` and `defer()`
- `values()` and `values_list()`

---

## Exercise 4: Advanced Database Operations

### Objective
Practice complex database operations including transactions, bulk operations, and custom SQL.

### Part A: Bulk Data Import
Create a management command to import blog posts from a CSV file:

```python
# management/commands/import_posts.py
from django.core.management.base import BaseCommand
import csv

class Command(BaseCommand):
    help = 'Import posts from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
    
    def handle(self, *args, **options):
        # TODO: Implement bulk import with error handling
        pass
```

### Part B: Transaction Management
Implement a function to transfer all posts from one author to another:

```python
def transfer_posts(from_author_id, to_author_id):
    """
    Transfer all posts from one author to another.
    Update post counts and handle any errors.
    """
    # TODO: Implement with proper transaction handling
    pass
```

### Part C: Database Views
Create a database view for post statistics:

```sql
-- Create a view that shows:
-- - Author name
-- - Number of posts
-- - Average post length
-- - Latest post date
-- - Total comments received
```

### Part D: Custom Aggregation
Write queries to calculate:
1. Monthly post creation statistics
2. Author activity scores (based on posts and comments)
3. Tag popularity trends over time
4. Category distribution percentages

---

## Exercise 5: Migration Scenarios

### Objective
Practice handling complex migration scenarios safely.

### Scenario 1: Adding Non-Nullable Field
You need to add a `slug` field to the `Post` model that must be unique and non-nullable.

### Tasks
1. Create a migration that:
   - Adds the field as nullable first
   - Populates existing records with generated slugs
   - Makes the field non-nullable and unique
2. Handle potential slug conflicts
3. Provide a reverse migration

### Scenario 2: Model Restructuring
You need to split the `Post` model into `Post` and `PostContent` to support versioning.

### Tasks
1. Create new `PostContent` model
2. Migrate existing data
3. Update relationships
4. Ensure data integrity throughout the process

### Scenario 3: Changing Relationship Types
Convert a ForeignKey relationship to ManyToMany (e.g., posts can belong to multiple categories).

### Tasks
1. Create intermediate model
2. Migrate existing relationships
3. Update application code
4. Remove old relationship

---

## Exercise 6: Performance Monitoring

### Objective
Learn to identify and monitor database performance issues.

### Setup
1. Install Django Debug Toolbar
2. Create a dataset with realistic size (1000+ posts, 100+ authors)
3. Set up logging for slow queries

### Tasks
1. Create views that demonstrate common performance problems
2. Use Django Debug Toolbar to identify issues
3. Implement solutions and measure improvements
4. Create a performance monitoring dashboard

### Metrics to Track
- Query count per request
- Query execution time
- Database connection usage
- Cache hit rates
- Memory usage

---

## Solutions and Hints

### Exercise 1 Hints
- Use `related_name` consistently for reverse relationships
- Consider using `select_related` for ForeignKey relationships
- Use `prefetch_related` for ManyToMany relationships
- Don't forget to create indexes on frequently queried fields

### Exercise 2 Hints
- Use `through` models for complex many-to-many relationships
- Consider using database constraints for data integrity
- Implement model methods for common calculations
- Use database functions for aggregations

### Exercise 3 Hints
- Start by counting queries with Django Debug Toolbar
- Use `select_related` for single-valued relationships
- Use `prefetch_related` for multi-valued relationships
- Consider using `Prefetch` objects for complex prefetching

### Exercise 4 Hints
- Use `bulk_create` for large data imports
- Always use transactions for related operations
- Consider using `update_or_create` for upsert operations
- Use raw SQL sparingly and safely

### Exercise 5 Hints
- Always test migrations on a copy of production data
- Use `RunPython` for data migrations
- Consider using `SeparateDatabaseAndState` for complex changes
- Document migration dependencies clearly

### Exercise 6 Hints
- Set `DEBUG = True` and install django-debug-toolbar
- Use `django.db.backends` logger to see all queries
- Consider using `django-silk` for production monitoring
- Profile both development and production-like environments

## Additional Resources

- [Django ORM Documentation](https://docs.djangoproject.com/en/stable/topics/db/)
- [Database Optimization Guide](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [Migration Documentation](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)