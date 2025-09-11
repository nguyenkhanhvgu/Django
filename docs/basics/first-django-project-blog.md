# Building Your First Django Project: A Blog Application

## Introduction

In this tutorial, you'll build a complete blog application from scratch using Django. This project will introduce you to Django's core concepts including models, views, templates, and URL routing through hands-on development.

By the end of this tutorial, you'll have:
- A fully functional blog with posts and comments
- Understanding of Django's MTV (Model-Template-View) architecture
- Experience with Django forms, database operations, and template rendering
- A foundation for building more complex Django applications

## Prerequisites

Before starting this tutorial, make sure you have:
- Completed the Django setup and installation guide
- Basic understanding of Python programming
- Familiarity with HTML and CSS basics
- Django development environment ready

## Project Overview

Our blog application will include:
- **Blog posts** with title, content, author, and publication date
- **Comment system** for reader engagement
- **Admin interface** for content management
- **User-friendly URLs** and navigation
- **Responsive templates** for different devices

## Step 1: Creating the Django Project

Let's start by creating a new Django project called `myblog`:

```bash
# Create the project
django-admin startproject myblog
cd myblog

# Create a virtual environment (if not already done)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Django
pip install django

# Verify the installation
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to see the Django welcome page.

**Commit Point 1**: Initial project setup
```bash
git init
git add .
git commit -m "Initial Django project setup"
```

## Step 2: Creating the Blog App

Django projects are organized into apps. Let's create our blog app:

```bash
python manage.py startapp blog
```

Add the app to your `INSTALLED_APPS` in `myblog/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',  # Add this line
]
```

**Commit Point 2**: Blog app creation
```bash
git add .
git commit -m "Create blog app and add to INSTALLED_APPS"
```

## Step 3: Creating the Blog Models

Models define the structure of your data. Let's create models for blog posts and comments.

Edit `blog/models.py`:

```python
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('published', 'Published')], default='draft')

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
```

Create and apply migrations:

```bash
python manage.py makemigrations blog
python manage.py migrate
```

**Commit Point 3**: Blog models creation
```bash
git add .
git commit -m "Create Post and Comment models with migrations"
```

## Step 4: Setting Up the Admin Interface

Django's admin interface allows easy content management. Let's register our models.

Edit `blog/admin.py`:

```python
from django.contrib import admin
from .models import Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
```

Create a superuser account:

```bash
python manage.py createsuperuser
```

**Commit Point 4**: Admin interface setup
```bash
git add .
git commit -m "Configure admin interface for Post and Comment models"
```

## Step 5: Creating Views

Views handle the logic for displaying content. Let's create views for our blog.

Edit `blog/views.py`:

```python
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .models import Post, Comment
from .forms import CommentForm

def post_list(request):
    object_list = Post.objects.filter(status='published')
    paginator = Paginator(object_list, 3)  # 3 posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    
    new_comment = None
    
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()
    
    return render(request, 'blog/post/detail.html', {
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form
    })

class PostListView(ListView):
    queryset = Post.objects.filter(status='published')
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
```

**Commit Point 5**: Views creation
```bash
git add .
git commit -m "Create post list and detail views with pagination"
```## S
tep 6: Creating Forms

Forms handle user input. Let's create a form for comments.

Create `blog/forms.py`:

```python
from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
```

**Commit Point 6**: Forms creation
```bash
git add .
git commit -m "Create CommentForm for user comments"
```

## Step 7: URL Configuration

URLs map web requests to views. Let's configure our URLs.

Create `blog/urls.py`:

```python
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Post views
    path('', views.post_list, name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
]
```

Update the main `myblog/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls', namespace='blog')),
    path('', include('blog.urls', namespace='blog')),  # Root URL points to blog
]
```

**Commit Point 7**: URL configuration
```bash
git add .
git commit -m "Configure URLs for blog views"
```

## Step 8: Creating Templates

Templates define how content is displayed. Let's create our HTML templates.

Create the template directory structure:
```
blog/templates/blog/
├── base.html
└── post/
    ├── list.html
    └── detail.html
```

Create `blog/templates/blog/base.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'blog:post_list' %}">My Blog</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8">
                {% block content %}
                {% endblock %}
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5>About</h5>
                    </div>
                    <div class="card-body">
                        <p>This is my personal blog where I share my thoughts and experiences.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

Create `blog/templates/blog/post/list.html`:

```html
{% extends "blog/base.html" %}

{% block title %}My Blog{% endblock %}

{% block content %}
    <h1>My Blog</h1>
    {% for post in posts %}
        <div class="card mb-4">
            <div class="card-body">
                <h2 class="card-title">
                    <a href="{{ post.get_absolute_url }}" class="text-decoration-none">{{ post.title }}</a>
                </h2>
                <p class="card-text text-muted">
                    Published {{ post.publish }} by {{ post.author }}
                </p>
                <p class="card-text">{{ post.body|truncatewords:30|linebreaks }}</p>
                <a href="{{ post.get_absolute_url }}" class="btn btn-primary">Read more</a>
            </div>
        </div>
    {% endfor %}
    
    {% include "pagination.html" with page=posts %}
{% endblock %}
```

Create `blog/templates/blog/post/detail.html`:

```html
{% extends "blog/base.html" %}

{% block title %}{{ post.title }}{% endblock %}

{% block content %}
    <article>
        <h1>{{ post.title }}</h1>
        <p class="text-muted">
            Published {{ post.publish }} by {{ post.author }}
        </p>
        <div class="mt-3">
            {{ post.body|linebreaks }}
        </div>
    </article>
    
    <hr>
    
    <div class="mt-4">
        <h3>Comments ({{ comments.count }})</h3>
        
        {% for comment in comments %}
            <div class="card mb-3">
                <div class="card-body">
                    <h6 class="card-subtitle mb-2 text-muted">
                        {{ comment.name }} - {{ comment.created }}
                    </h6>
                    <p class="card-text">{{ comment.body|linebreaks }}</p>
                </div>
            </div>
        {% empty %}
            <p>No comments yet.</p>
        {% endfor %}
        
        <hr>
        
        <h4>Add a comment</h4>
        {% if new_comment %}
            <div class="alert alert-success">
                Your comment has been added successfully!
            </div>
        {% else %}
            <form method="post">
                {% csrf_token %}
                <div class="mb-3">
                    <label for="{{ comment_form.name.id_for_label }}" class="form-label">Name</label>
                    {{ comment_form.name }}
                </div>
                <div class="mb-3">
                    <label for="{{ comment_form.email.id_for_label }}" class="form-label">Email</label>
                    {{ comment_form.email }}
                </div>
                <div class="mb-3">
                    <label for="{{ comment_form.body.id_for_label }}" class="form-label">Comment</label>
                    {{ comment_form.body }}
                </div>
                <button type="submit" class="btn btn-primary">Add Comment</button>
            </form>
        {% endif %}
    </div>
{% endblock %}
```

Create `blog/templates/pagination.html`:

```html
<nav aria-label="Page navigation">
    <ul class="pagination justify-content-center">
        {% if page.has_previous %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page.previous_page_number }}">Previous</a>
            </li>
        {% endif %}
        
        <li class="page-item active">
            <span class="page-link">
                Page {{ page.number }} of {{ page.paginator.num_pages }}
            </span>
        </li>
        
        {% if page.has_next %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page.next_page_number }}">Next</a>
            </li>
        {% endif %}
    </ul>
</nav>
```

**Commit Point 8**: Templates creation
```bash
git add .
git commit -m "Create HTML templates for blog posts and comments"
```

## Step 9: Testing Your Blog

Now let's test our blog application:

1. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

2. **Access the admin interface** at `http://127.0.0.1:8000/admin/`:
   - Log in with your superuser credentials
   - Create a few blog posts with status "Published"

3. **View your blog** at `http://127.0.0.1:8000/`:
   - You should see your published posts
   - Click on a post to view details and add comments

**Commit Point 9**: Final working blog
```bash
git add .
git commit -m "Complete working blog application with posts and comments"
```

## Step 10: Adding Static Files (Optional Enhancement)

For better styling, let's add custom CSS:

Create `blog/static/blog/css/blog.css`:

```css
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f8f9fa;
}

.navbar-brand {
    font-weight: bold;
}

.card {
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border: none;
}

.card-title a {
    color: #333;
}

.card-title a:hover {
    color: #007bff;
}

.btn-primary {
    background-color: #007bff;
    border-color: #007bff;
}

.btn-primary:hover {
    background-color: #0056b3;
    border-color: #0056b3;
}

.text-muted {
    color: #6c757d !important;
}

.pagination .page-link {
    color: #007bff;
}

.pagination .page-item.active .page-link {
    background-color: #007bff;
    border-color: #007bff;
}
```

Update your base template to include the CSS:

```html
<!-- Add this line in the <head> section of base.html -->
<link rel="stylesheet" type="text/css" href="{% load static %}{% static 'blog/css/blog.css' %}">
```

**Commit Point 10**: Custom styling
```bash
git add .
git commit -m "Add custom CSS styling for better appearance"
```

## Congratulations!

You've successfully built your first Django blog application! Your blog now includes:

✅ **Models**: Post and Comment models with proper relationships  
✅ **Views**: Function-based and class-based views with pagination  
✅ **Templates**: Responsive HTML templates with Bootstrap styling  
✅ **Forms**: Comment form with validation  
✅ **Admin Interface**: Easy content management  
✅ **URL Routing**: Clean, SEO-friendly URLs  

## Next Steps

Now that you have a working blog, consider these enhancements:

1. **Add user authentication** for post authors
2. **Implement post categories and tags**
3. **Add search functionality**
4. **Create an RSS feed**
5. **Add social media sharing buttons**
6. **Implement email notifications for comments**

## Key Concepts Learned

Through building this blog, you've learned:

- **Django Project Structure**: How apps, models, views, and templates work together
- **Database Operations**: Creating models, migrations, and using the ORM
- **Form Handling**: Processing user input and validation
- **Template System**: Rendering dynamic content with Django templates
- **URL Routing**: Mapping URLs to views
- **Admin Interface**: Using Django's built-in admin for content management

This foundation will serve you well as you continue learning Django and building more complex applications!