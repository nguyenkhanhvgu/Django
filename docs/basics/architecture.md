# Django Architecture and Core Concepts

## Table of Contents
- [Understanding Django's MTV Pattern](#understanding-djangos-mtv-pattern)
- [Django Project Structure](#django-project-structure)
- [Models: Your Data Layer](#models-your-data-layer)
- [Views: Your Logic Layer](#views-your-logic-layer)
- [Templates: Your Presentation Layer](#templates-your-presentation-layer)
- [URL Routing: Connecting It All](#url-routing-connecting-it-all)
- [How It All Works Together](#how-it-all-works-together)
- [Interactive Exercises](#interactive-exercises)

## Understanding Django's MTV Pattern

Django follows the **Model-Template-View (MTV)** architectural pattern, which is Django's interpretation of the traditional Model-View-Controller (MVC) pattern. Understanding this pattern is crucial for building well-structured Django applications.

### MTV vs MVC Comparison

```
Traditional MVC          Django MTV
┌─────────────┐         ┌─────────────┐
│    Model    │   ←→    │    Model    │
│ (Data Logic)│         │ (Data Logic)│
└─────────────┘         └─────────────┘
       ↕                       ↕
┌─────────────┐         ┌─────────────┐
│    View     │   ←→    │  Template   │
│(Presentation)│         │(Presentation)│
└─────────────┘         └─────────────┘
       ↕                       ↕
┌─────────────┐         ┌─────────────┐
│ Controller  │   ←→    │    View     │
│(Logic/Flow) │         │(Logic/Flow) │
└─────────────┘         └─────────────┘
```

### The MTV Components

**Model (M)**
- Defines your data structure
- Handles database operations
- Contains business logic related to data
- Maps to database tables

**Template (T)**
- Defines how data is presented
- Contains HTML with Django template language
- Handles the user interface
- Separates presentation from logic

**View (V)**
- Contains application logic
- Processes requests and returns responses
- Connects models and templates
- Handles user interactions

## Django Project Structure

When you create a Django project, you get a specific directory structure that supports the MTV pattern:

```
myproject/
├── myproject/              # Project configuration
│   ├── __init__.py
│   ├── settings.py         # Project settings
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── myapp/                 # Django application
│   ├── __init__.py
│   ├── admin.py           # Admin interface configuration
│   ├── apps.py            # App configuration
│   ├── models.py          # Models (M in MTV)
│   ├── views.py           # Views (V in MTV)
│   ├── urls.py            # App-specific URLs
│   ├── tests.py           # Unit tests
│   └── migrations/        # Database migrations
│       └── __init__.py
├── templates/             # Templates (T in MTV)
│   └── myapp/
│       └── index.html
├── static/                # Static files (CSS, JS, images)
│   └── myapp/
│       ├── css/
│       ├── js/
│       └── images/
└── manage.py              # Django management script
```

## Models: Your Data Layer

Models define the structure of your data and provide an abstraction layer for database operations. They're Python classes that inherit from `django.db.models.Model`.

### Basic Model Example

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
    
    class Meta:
        verbose_name_plural = "Categories"

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
```

### Common Field Types

```python
# Text fields
title = models.CharField(max_length=200)          # Short text
content = models.TextField()                      # Long text
slug = models.SlugField(max_length=200)          # URL-friendly text

# Numeric fields
price = models.DecimalField(max_digits=10, decimal_places=2)
quantity = models.IntegerField()
rating = models.FloatField()

# Date and time fields
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
publish_date = models.DateField()

# Boolean fields
is_active = models.BooleanField(default=True)

# Relationship fields
author = models.ForeignKey(User, on_delete=models.CASCADE)
tags = models.ManyToManyField('Tag')
profile = models.OneToOneField(User, on_delete=models.CASCADE)
```

### Model Methods and Properties

```python
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        """String representation of the model"""
        return self.title
    
    def get_absolute_url(self):
        """Return the URL for this post"""
        from django.urls import reverse
        return reverse('post_detail', kwargs={'pk': self.pk})
    
    @property
    def word_count(self):
        """Calculate word count of the content"""
        return len(self.content.split())
    
    def save(self, *args, **kwargs):
        """Override save method for custom logic"""
        # Custom logic before saving
        super().save(*args, **kwargs)
        # Custom logic after saving
```

## Views: Your Logic Layer

Views handle the logic of your application. They receive HTTP requests, process them (often involving models), and return HTTP responses (usually rendered templates).

### Function-Based Views

```python
# views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Post, Category

def post_list(request):
    """Display a list of all published posts"""
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    categories = Category.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories,
        'page_title': 'Latest Posts'
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, post_id):
    """Display a single post"""
    post = get_object_or_404(Post, id=post_id, is_published=True)
    
    context = {
        'post': post,
        'page_title': post.title
    }
    return render(request, 'blog/post_detail.html', context)

def category_posts(request, category_id):
    """Display posts from a specific category"""
    category = get_object_or_404(Category, id=category_id)
    posts = Post.objects.filter(category=category, is_published=True)
    
    context = {
        'category': category,
        'posts': posts,
        'page_title': f'Posts in {category.name}'
    }
    return render(request, 'blog/category_posts.html', context)
```

### Class-Based Views

```python
# views.py
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Post

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(is_published=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.filter(is_published=True)
```

### Handling Forms in Views

```python
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PostForm

def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm()
    
    return render(request, 'blog/create_post.html', {'form': form})
```

## Templates: Your Presentation Layer

Templates define how your data is presented to users. Django uses its own template language that allows you to display dynamic content while keeping logic separate from presentation.

### Basic Template Structure

```html
<!-- templates/blog/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Blog{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'blog/css/style.css' %}">
</head>
<body>
    <header>
        <nav>
            <a href="{% url 'post_list' %}">Home</a>
            <a href="{% url 'about' %}">About</a>
        </nav>
    </header>
    
    <main>
        {% if messages %}
            <div class="messages">
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        {% endif %}
        
        {% block content %}
        {% endblock %}
    </main>
    
    <footer>
        <p>&copy; 2024 My Blog. All rights reserved.</p>
    </footer>
</body>
</html>
```

### Template Inheritance

```html
<!-- templates/blog/post_list.html -->
{% extends 'blog/base.html' %}
{% load static %}

{% block title %}{{ page_title }} - {{ block.super }}{% endblock %}

{% block content %}
<div class="container">
    <h1>{{ page_title }}</h1>
    
    <div class="sidebar">
        <h3>Categories</h3>
        <ul>
            {% for category in categories %}
                <li>
                    <a href="{% url 'category_posts' category.id %}">
                        {{ category.name }}
                    </a>
                </li>
            {% empty %}
                <li>No categories available.</li>
            {% endfor %}
        </ul>
    </div>
    
    <div class="posts">
        {% for post in posts %}
            <article class="post-preview">
                <h2>
                    <a href="{% url 'post_detail' post.id %}">
                        {{ post.title }}
                    </a>
                </h2>
                <p class="post-meta">
                    By {{ post.author.username }} on {{ post.created_at|date:"F d, Y" }}
                    {% if post.category %}
                        in <a href="{% url 'category_posts' post.category.id %}">
                            {{ post.category.name }}
                        </a>
                    {% endif %}
                </p>
                <p>{{ post.content|truncatewords:50 }}</p>
                <a href="{% url 'post_detail' post.id %}" class="read-more">
                    Read more...
                </a>
            </article>
        {% empty %}
            <p>No posts available.</p>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

### Template Tags and Filters

```html
<!-- Common template tags and filters -->

<!-- Variables -->
{{ post.title }}
{{ post.created_at }}

<!-- Filters -->
{{ post.title|upper }}
{{ post.content|truncatewords:20 }}
{{ post.created_at|date:"F d, Y" }}
{{ post.content|linebreaks }}

<!-- Control structures -->
{% if post.is_published %}
    <p>This post is published</p>
{% else %}
    <p>This post is a draft</p>
{% endif %}

{% for post in posts %}
    <h2>{{ post.title }}</h2>
{% empty %}
    <p>No posts found</p>
{% endfor %}

<!-- URL generation -->
<a href="{% url 'post_detail' post.id %}">{{ post.title }}</a>

<!-- Static files -->
{% load static %}
<img src="{% static 'blog/images/logo.png' %}" alt="Logo">

<!-- Comments -->
{# This is a comment and won't be rendered #}
```

## URL Routing: Connecting It All

URL routing connects URLs to views, allowing users to access different parts of your application through specific URLs.

### Project-Level URLs

```python
# myproject/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### App-Level URLs

```python
# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Function-based views
    path('', views.post_list, name='post_list'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('create/', views.create_post, name='create_post'),
    
    # Class-based views
    path('posts/', views.PostListView.as_view(), name='post_list_cbv'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail_cbv'),
    
    # URL patterns with different parameter types
    path('posts/<slug:slug>/', views.post_by_slug, name='post_by_slug'),
    path('archive/<int:year>/', views.posts_by_year, name='posts_by_year'),
    path('archive/<int:year>/<int:month>/', views.posts_by_month, name='posts_by_month'),
]
```

### URL Pattern Types

```python
# Different URL pattern examples
urlpatterns = [
    # Integer parameter
    path('post/<int:id>/', views.post_detail),
    
    # String parameter (default)
    path('category/<str:name>/', views.category_detail),
    
    # Slug parameter (letters, numbers, hyphens, underscores)
    path('post/<slug:slug>/', views.post_by_slug),
    
    # UUID parameter
    path('user/<uuid:user_id>/', views.user_profile),
    
    # Path parameter (matches any string including slashes)
    path('files/<path:file_path>/', views.serve_file),
    
    # Optional parameters with defaults
    path('posts/', views.post_list, {'page': 1}),
    path('posts/page/<int:page>/', views.post_list),
]
```

## How It All Works Together

Let's trace through a complete request-response cycle to see how all components work together:

### Request Flow Diagram

```
1. User Request
   ↓
2. URL Dispatcher (urls.py)
   ↓
3. View Function/Class (views.py)
   ↓
4. Model Interaction (models.py)
   ↓
5. Template Rendering (templates/)
   ↓
6. HTTP Response
```

### Step-by-Step Example

1. **User visits**: `http://localhost:8000/post/1/`

2. **URL Resolution**: Django checks `urls.py` files:
   ```python
   # Matches: path('post/<int:post_id>/', views.post_detail, name='post_detail')
   ```

3. **View Execution**: Django calls the `post_detail` view:
   ```python
   def post_detail(request, post_id):
       post = get_object_or_404(Post, id=post_id, is_published=True)
       context = {'post': post}
       return render(request, 'blog/post_detail.html', context)
   ```

4. **Model Query**: The view queries the database through the model:
   ```python
   # Django ORM translates this to SQL:
   # SELECT * FROM blog_post WHERE id = 1 AND is_published = True;
   ```

5. **Template Rendering**: Django renders the template with context data:
   ```html
   <!-- post_detail.html -->
   <h1>{{ post.title }}</h1>
   <p>{{ post.content }}</p>
   ```

6. **Response**: Django returns the rendered HTML to the user's browser.

## Interactive Exercises

### Exercise 1: Create Your First Model

Create a simple `Book` model with the following fields:
- `title` (CharField, max_length=200)
- `author` (CharField, max_length=100)
- `isbn` (CharField, max_length=13)
- `publication_date` (DateField)
- `pages` (IntegerField)
- `is_available` (BooleanField, default=True)

**Solution:**
```python
# models.py
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)
    publication_date = models.DateField()
    pages = models.IntegerField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
```

### Exercise 2: Create a Simple View

Create a view that displays all available books:

**Solution:**
```python
# views.py
from django.shortcuts import render
from .models import Book

def book_list(request):
    books = Book.objects.filter(is_available=True)
    context = {'books': books}
    return render(request, 'library/book_list.html', context)
```

### Exercise 3: Create a Template

Create a template to display the book list:

**Solution:**
```html
<!-- templates/library/book_list.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Available Books</title>
</head>
<body>
    <h1>Available Books</h1>
    <ul>
        {% for book in books %}
            <li>
                <strong>{{ book.title }}</strong> by {{ book.author }}
                <br>
                ISBN: {{ book.isbn }} | Pages: {{ book.pages }}
                <br>
                Published: {{ book.publication_date|date:"F d, Y" }}
            </li>
        {% empty %}
            <li>No books available.</li>
        {% endfor %}
    </ul>
</body>
</html>
```

### Exercise 4: Configure URLs

Create URL patterns for your book views:

**Solution:**
```python
# library/urls.py
from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.book_list, name='book_list'),
]

# myproject/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('library/', include('library.urls')),
]
```

### Common Beginner Mistakes and Solutions

1. **Forgetting to run migrations**
   ```bash
   # After creating/modifying models, always run:
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Template not found errors**
   - Check `TEMPLATES` setting in `settings.py`
   - Ensure template path is correct
   - Verify app is in `INSTALLED_APPS`

3. **Import errors in views**
   ```python
   # Correct imports
   from django.shortcuts import render, get_object_or_404
   from .models import YourModel
   ```

4. **URL pattern not matching**
   - Check parameter types (`<int:id>` vs `<str:id>`)
   - Verify URL order (more specific patterns first)
   - Use `reverse()` and `{% url %}` for URL generation

## Next Steps

Now that you understand Django's architecture and core concepts, you're ready to:

1. Build your first complete Django project (covered in the next tutorial)
2. Learn about forms and user input handling
3. Explore Django's admin interface
4. Understand database relationships in depth

The key to mastering Django is practice. Try building small projects that use all these components together, and don't be afraid to experiment with different approaches!