# Database Relationships Demo

This Django project demonstrates advanced database relationships, query optimization, and ORM techniques covered in the intermediate database management tutorial.

## Project Structure

```
database-relationships-demo/
├── manage.py
├── requirements.txt
├── blog_system/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── blog/
│   ├── models.py          # Main models with relationships
│   ├── views.py           # Optimized views
│   ├── admin.py           # Admin configuration
│   ├── managers.py        # Custom managers and querysets
│   └── migrations/
├── ecommerce/
│   ├── models.py          # E-commerce example models
│   └── views.py           # Product catalog views
└── management/
    └── commands/
        ├── create_sample_data.py
        └── import_posts.py
```

## Features Demonstrated

### 1. Model Relationships
- **One-to-Many**: Posts → Categories, Posts → Comments
- **One-to-One**: User → UserProfile
- **Many-to-Many**: Posts ↔ Tags
- **Self-referencing**: Category hierarchy
- **Through models**: BookAuthor with additional fields

### 2. Query Optimization
- `select_related()` for ForeignKey relationships
- `prefetch_related()` for ManyToMany relationships
- Custom `Prefetch` objects
- Database functions and aggregations
- Bulk operations

### 3. Advanced ORM Features
- Custom managers and querysets
- Model methods and properties
- Database constraints and indexes
- Raw SQL integration
- Transaction management

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create sample data:
```bash
python manage.py create_sample_data
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Key Examples

### Efficient Post Listing
```python
# Optimized query that loads posts with related data in minimal queries
posts = Post.objects.select_related('author', 'category').prefetch_related('tags').all()
```

### Complex Aggregations
```python
# Get author statistics with post count and average content length
author_stats = User.objects.annotate(
    post_count=Count('posts'),
    avg_content_length=Avg('posts__content_length'),
    latest_post=Max('posts__created_at')
).filter(post_count__gt=0)
```

### Bulk Operations
```python
# Efficiently create multiple posts
posts = [
    Post(title=f"Post {i}", content=f"Content {i}", author=author, category=category)
    for i in range(1000)
]
Post.objects.bulk_create(posts, batch_size=100)
```

## Performance Testing

Use Django Debug Toolbar to monitor query performance:

1. Install django-debug-toolbar (included in requirements.txt)
2. Visit `/blog/posts/` to see optimized queries
3. Visit `/blog/posts-slow/` to see unoptimized queries
4. Compare query counts and execution times

## Database Schema

The project includes models that demonstrate:

- **Blog System**: Posts, Categories, Tags, Comments, UserProfiles
- **E-commerce**: Products, Categories, Variants, Reviews, Orders
- **Library System**: Books, Authors, Publishers (with through models)

## Management Commands

### Create Sample Data
```bash
python manage.py create_sample_data --posts 1000 --authors 50 --tags 100
```

### Import Posts from CSV
```bash
python manage.py import_posts data/posts.csv
```

### Performance Test
```bash
python manage.py performance_test
```

## Learning Objectives

After exploring this project, you should understand:

1. How to design efficient database relationships
2. When to use each type of Django relationship
3. How to optimize database queries
4. How to use custom managers and querysets
5. How to handle bulk operations efficiently
6. How to use database transactions safely
7. How to monitor and improve query performance

## Next Steps

- Explore the Django REST Framework tutorial to learn API development
- Check out the deployment tutorial to learn production best practices
- Try the advanced Django patterns tutorial for more complex scenarios