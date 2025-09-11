# Django Architecture Demo

This directory contains comprehensive code examples demonstrating Django's MTV (Model-Template-View) architecture pattern. These examples accompany the Django Architecture tutorial and provide practical implementations of core Django concepts.

## 📁 Directory Structure

```
architecture-demo/
├── models.py              # Model examples and relationships
├── views.py               # Function-based and class-based views
├── urls.py                # URL routing patterns
├── templates/             # Template examples
│   └── blog/
│       ├── base.html      # Base template with inheritance
│       └── post_list.html # Post listing template
└── README.md              # This file
```

## 🎯 What You'll Learn

### Models (Data Layer)
- **Basic Model Structure**: Field types, constraints, and validation
- **Model Relationships**: ForeignKey, ManyToMany, OneToOne
- **Model Methods**: Custom properties, methods, and managers
- **Meta Options**: Ordering, indexing, and verbose names
- **Database Operations**: QuerySets, filtering, and aggregation

### Views (Logic Layer)
- **Function-Based Views**: Request handling, context building, responses
- **Class-Based Views**: ListView, DetailView, CreateView, UpdateView
- **View Patterns**: Pagination, filtering, search functionality
- **Authentication**: Login requirements and permissions
- **Error Handling**: 404 handling and custom error pages

### Templates (Presentation Layer)
- **Template Inheritance**: Base templates and block overrides
- **Template Tags**: Loops, conditionals, URL generation
- **Template Filters**: Data formatting and transformation
- **Context Variables**: Accessing data from views
- **Static Files**: CSS, JavaScript, and image handling

### URL Routing (Connection Layer)
- **URL Patterns**: Path types and parameter capture
- **Named URLs**: URL reversing and generation
- **App Namespacing**: Organizing URLs by application
- **Regular Expressions**: Advanced pattern matching
- **URL Parameters**: Passing data through URLs

## 🚀 Key Features Demonstrated

### 1. Complete Blog System
- Post creation, listing, and detail views
- Category and tag organization
- Comment system with nested replies
- Search and filtering functionality
- User authentication integration

### 2. Advanced QuerySets
```python
# Complex filtering and relationships
posts = Post.objects.filter(
    status='published',
    category__name__icontains='django'
).select_related('author', 'category').prefetch_related('tags')
```

### 3. Template Inheritance
```html
<!-- Base template with blocks -->
{% block content %}
    <!-- Child templates override this -->
{% endblock %}
```

### 4. URL Patterns
```python
# Various URL pattern types
path('post/<slug:slug>/', views.post_detail, name='post_detail')
path('category/<int:pk>/', views.category_detail, name='category_detail')
re_path(r'^archive/(?P<year>[0-9]{4})/$', views.posts_by_year)
```

## 📋 Code Examples Included

### Model Examples
- **Category Model**: Basic model with string representation
- **Post Model**: Complex model with multiple field types and relationships
- **Comment Model**: Self-referencing foreign key for nested comments
- **Tag Model**: Many-to-many relationship demonstration
- **Custom Managers**: Filtered querysets and custom methods

### View Examples
- **post_list()**: Pagination, filtering, and search
- **post_detail()**: Object retrieval and related data
- **PostListView**: Class-based list view with customization
- **PostDetailView**: Class-based detail view with context
- **API Views**: JSON response handling

### Template Examples
- **base.html**: Complete base template with navigation, messages, and blocks
- **post_list.html**: Pagination, filtering, and responsive design
- **Template Tags**: URL generation, loops, conditionals, and filters
- **Context Usage**: Accessing view data and user information

### URL Examples
- **Basic Patterns**: Simple path matching
- **Parameter Capture**: Integer, slug, and string parameters
- **Regular Expressions**: Advanced pattern matching
- **Namespacing**: App-level URL organization

## 🛠️ How to Use These Examples

### 1. Study the Code Structure
Start with `models.py` to understand the data structure, then move to `views.py` to see how data is processed, and finally examine the templates to see how data is presented.

### 2. Follow the Request Flow
Trace a complete request from URL → View → Model → Template → Response:
1. URL pattern matches in `urls.py`
2. View function/class processes request in `views.py`
3. Model queries database in `models.py`
4. Template renders HTML in `templates/`
5. Response sent to browser

### 3. Experiment with Modifications
- Add new fields to models
- Create additional views
- Modify templates
- Add new URL patterns

### 4. Run the Code
While these are example files, you can integrate them into a Django project:

```bash
# Create a new Django project
django-admin startproject myproject
cd myproject

# Create a blog app
python manage.py startapp blog

# Copy the example files to your app
# Add 'blog' to INSTALLED_APPS in settings.py
# Include blog URLs in main urls.py

# Create and run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser and run server
python manage.py createsuperuser
python manage.py runserver
```

## 🔍 Key Concepts Explained

### MTV Pattern Flow
```
1. User Request → URL Dispatcher
2. URL Dispatcher → View
3. View → Model (data retrieval)
4. Model → Database
5. Database → Model (data return)
6. Model → View (processed data)
7. View → Template (context data)
8. Template → View (rendered HTML)
9. View → User (HTTP response)
```

### Model Relationships
- **ForeignKey**: One-to-many (Post → Category)
- **ManyToManyField**: Many-to-many (Post ↔ Tag)
- **OneToOneField**: One-to-one (User → Profile)

### View Types
- **Function-Based Views**: Simple, explicit, flexible
- **Class-Based Views**: DRY, inheritance, built-in functionality

### Template Features
- **Inheritance**: Reusable base templates
- **Context**: Data from views
- **Tags**: Logic and control structures
- **Filters**: Data transformation

## 📚 Related Documentation

- [Django Models Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Views Documentation](https://docs.djangoproject.com/en/stable/topics/http/views/)
- [Django Templates Documentation](https://docs.djangoproject.com/en/stable/topics/templates/)
- [Django URL Dispatcher](https://docs.djangoproject.com/en/stable/topics/http/urls/)

## 🎓 Learning Path

1. **Start Here**: Read the main architecture tutorial in `docs/basics/architecture.md`
2. **Study Examples**: Examine the code files in this directory
3. **Practice**: Complete the exercises in `exercises/basics/architecture-exercises.md`
4. **Build**: Create your own Django project using these patterns
5. **Expand**: Add features like forms, authentication, and APIs

## 💡 Best Practices Demonstrated

- **Model Design**: Proper field types, relationships, and methods
- **View Organization**: Separation of concerns and DRY principles
- **Template Structure**: Inheritance and reusable components
- **URL Design**: RESTful patterns and meaningful names
- **Code Documentation**: Comments and docstrings
- **Error Handling**: Graceful failure and user feedback

## 🔧 Troubleshooting

### Common Issues
1. **Import Errors**: Check relative imports (`from .models import Post`)
2. **Template Not Found**: Verify template paths and INSTALLED_APPS
3. **URL Reverse Errors**: Ensure URL names match and use namespaces
4. **Migration Issues**: Run `makemigrations` after model changes

### Debug Tips
- Use Django's debug toolbar for development
- Check the Django shell for testing queries
- Use `print()` statements in views for debugging
- Examine the Django logs for error details

This architecture demo provides a solid foundation for understanding Django's MTV pattern and building robust web applications. Use these examples as a reference while building your own Django projects!