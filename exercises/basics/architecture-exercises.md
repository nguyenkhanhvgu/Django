# Django Architecture Interactive Exercises

## Overview
These exercises will help you practice Django's MTV (Model-Template-View) architecture concepts. Each exercise builds upon the previous one, starting with simple concepts and progressing to more complex implementations.

## Prerequisites
- Basic Python knowledge
- Django installed and configured
- Understanding of HTML basics

---

## Exercise 1: Understanding Models

### Objective
Create a simple model and understand Django's ORM basics.

### Task
Create a `Book` model for a library management system with the following requirements:

**Model Fields:**
- `title` - CharField with max length 200
- `author` - CharField with max length 100  
- `isbn` - CharField with max length 13, must be unique
- `publication_date` - DateField
- `pages` - PositiveIntegerField
- `is_available` - BooleanField with default True
- `created_at` - DateTimeField that auto-sets on creation
- `updated_at` - DateTimeField that auto-updates on save

**Additional Requirements:**
- Add a `__str__` method that returns the book title
- Add a `get_absolute_url` method
- Add a custom property `age_in_days` that calculates days since publication
- Add proper Meta class with ordering by title

### Starter Code
```python
# models.py
from django.db import models
from django.urls import reverse
from datetime import date

class Book(models.Model):
    # Add your fields here
    pass
    
    def __str__(self):
        # Add string representation
        pass
    
    def get_absolute_url(self):
        # Add URL generation
        pass
    
    @property
    def age_in_days(self):
        # Calculate days since publication
        pass
    
    class Meta:
        # Add meta options
        pass
```

### Solution
<details>
<summary>Click to reveal solution</summary>

```python
# models.py
from django.db import models
from django.urls import reverse
from datetime import date

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()
    pages = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('library:book_detail', kwargs={'pk': self.pk})
    
    @property
    def age_in_days(self):
        return (date.today() - self.publication_date).days
    
    class Meta:
        ordering = ['title']
```
</details>

### Test Your Understanding
1. What happens if you don't provide a default value for `is_available`?
2. What's the difference between `auto_now_add` and `auto_now`?
3. Why is the `isbn` field set to unique?

---

## Exercise 2: Creating Views

### Objective
Create function-based and class-based views to display and manipulate data.

### Task
Create views for the Book model with the following functionality:

**Required Views:**
1. `book_list` - Display all available books with pagination (5 books per page)
2. `book_detail` - Display a single book's details
3. `book_search` - Search books by title or author
4. `BookListView` - Class-based version of book_list
5. `BookDetailView` - Class-based version of book_detail

### Starter Code
```python
# views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Book

def book_list(request):
    # Implement book listing with pagination
    pass

def book_detail(request, pk):
    # Implement book detail view
    pass

def book_search(request):
    # Implement search functionality
    pass

class BookListView(ListView):
    # Implement class-based list view
    pass

class BookDetailView(DetailView):
    # Implement class-based detail view
    pass
```

### Solution
<details>
<summary>Click to reveal solution</summary>

```python
# views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Book

def book_list(request):
    books = Book.objects.filter(is_available=True).order_by('title')
    paginator = Paginator(books, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_books': books.count()
    }
    return render(request, 'library/book_list.html', context)

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    context = {'book': book}
    return render(request, 'library/book_detail.html', context)

def book_search(request):
    query = request.GET.get('q', '')
    books = []
    
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query),
            is_available=True
        )
    
    context = {
        'books': books,
        'query': query
    }
    return render(request, 'library/book_search.html', context)

class BookListView(ListView):
    model = Book
    template_name = 'library/book_list_cbv.html'
    context_object_name = 'books'
    paginate_by = 5
    
    def get_queryset(self):
        return Book.objects.filter(is_available=True).order_by('title')

class BookDetailView(DetailView):
    model = Book
    template_name = 'library/book_detail_cbv.html'
    context_object_name = 'book'
```
</details>

### Test Your Understanding
1. What's the difference between `render` and `get_object_or_404`?
2. When would you use class-based views over function-based views?
3. How does pagination work in Django?

---

## Exercise 3: Template Creation

### Objective
Create templates that properly display data and demonstrate template inheritance.

### Task
Create templates for your book views with the following requirements:

**Required Templates:**
1. `base.html` - Base template with navigation and common elements
2. `book_list.html` - Display paginated book list
3. `book_detail.html` - Display single book details
4. `book_search.html` - Search form and results

**Template Requirements:**
- Use template inheritance
- Include proper navigation
- Show pagination controls
- Display book information clearly
- Include search functionality
- Handle empty states

### Starter Code
```html
<!-- templates/library/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Library System{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <!-- Add navigation here -->
    </nav>
    
    <main class="container my-4">
        {% block content %}
        {% endblock %}
    </main>
</body>
</html>
```

### Solution
<details>
<summary>Click to reveal solution</summary>

```html
<!-- templates/library/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Library System{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'library:book_list' %}">Library</a>
            <div class="navbar-nav">
                <a class="nav-link" href="{% url 'library:book_list' %}">Books</a>
                <a class="nav-link" href="{% url 'library:book_search' %}">Search</a>
            </div>
        </div>
    </nav>
    
    <main class="container my-4">
        {% block content %}
        {% endblock %}
    </main>
</body>
</html>

<!-- templates/library/book_list.html -->
{% extends 'library/base.html' %}

{% block title %}Book List - {{ block.super }}{% endblock %}

{% block content %}
<h1>Available Books</h1>
<p>Total books: {{ total_books }}</p>

{% if page_obj %}
    <div class="row">
        {% for book in page_obj %}
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            <a href="{% url 'library:book_detail' book.pk %}">{{ book.title }}</a>
                        </h5>
                        <p class="card-text">
                            <strong>Author:</strong> {{ book.author }}<br>
                            <strong>Pages:</strong> {{ book.pages }}<br>
                            <strong>Published:</strong> {{ book.publication_date|date:"F d, Y" }}
                        </p>
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>
    
    <!-- Pagination -->
    {% if page_obj.has_other_pages %}
        <nav>
            <ul class="pagination justify-content-center">
                {% if page_obj.has_previous %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.previous_page_number }}">Previous</a>
                    </li>
                {% endif %}
                
                <li class="page-item active">
                    <span class="page-link">{{ page_obj.number }}</span>
                </li>
                
                {% if page_obj.has_next %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.next_page_number }}">Next</a>
                    </li>
                {% endif %}
            </ul>
        </nav>
    {% endif %}
{% else %}
    <p>No books available.</p>
{% endif %}
{% endblock %}

<!-- templates/library/book_detail.html -->
{% extends 'library/base.html' %}

{% block title %}{{ book.title }} - {{ block.super }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h1>{{ book.title }}</h1>
        <div class="card">
            <div class="card-body">
                <p><strong>Author:</strong> {{ book.author }}</p>
                <p><strong>ISBN:</strong> {{ book.isbn }}</p>
                <p><strong>Publication Date:</strong> {{ book.publication_date|date:"F d, Y" }}</p>
                <p><strong>Pages:</strong> {{ book.pages }}</p>
                <p><strong>Age:</strong> {{ book.age_in_days }} days old</p>
                <p><strong>Status:</strong> 
                    {% if book.is_available %}
                        <span class="badge bg-success">Available</span>
                    {% else %}
                        <span class="badge bg-danger">Not Available</span>
                    {% endif %}
                </p>
            </div>
        </div>
        <a href="{% url 'library:book_list' %}" class="btn btn-secondary mt-3">Back to List</a>
    </div>
</div>
{% endblock %}
```
</details>

---

## Exercise 4: URL Configuration

### Objective
Create proper URL patterns that connect views to URLs.

### Task
Create URL configurations for your library app with the following requirements:

**Required URLs:**
- `/` - Book list (function-based view)
- `/book/<int:pk>/` - Book detail (function-based view)  
- `/search/` - Book search
- `/cbv/` - Book list (class-based view)
- `/cbv/book/<int:pk>/` - Book detail (class-based view)

### Starter Code
```python
# library/urls.py
from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Add your URL patterns here
]

# main/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add library URLs here
]
```

### Solution
<details>
<summary>Click to reveal solution</summary>

```python
# library/urls.py
from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('search/', views.book_search, name='book_search'),
    path('cbv/', views.BookListView.as_view(), name='book_list_cbv'),
    path('cbv/book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail_cbv'),
]

# main/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('library/', include('library.urls')),
]
```
</details>

---

## Exercise 5: Complete Integration

### Objective
Put it all together and test the complete MTV flow.

### Task
1. Create and run migrations for your Book model
2. Create some sample data using Django shell
3. Test all your views and templates
4. Add error handling for edge cases

### Commands to Run
```bash
# Create migrations
python manage.py makemigrations library

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Sample Data Creation
```python
# In Django shell: python manage.py shell
from library.models import Book
from datetime import date

# Create sample books
Book.objects.create(
    title="Django for Beginners",
    author="William Vincent",
    isbn="9781735467207",
    publication_date=date(2022, 1, 1),
    pages=350
)

Book.objects.create(
    title="Two Scoops of Django",
    author="Daniel Roy Greenfeld",
    isbn="9780692915729",
    publication_date=date(2020, 5, 15),
    pages=532
)
```

### Testing Checklist
- [ ] Book list displays correctly with pagination
- [ ] Book detail shows all information
- [ ] Search functionality works
- [ ] Navigation links work properly
- [ ] Empty states are handled
- [ ] URLs generate correctly
- [ ] Class-based views work identically to function-based views

---

## Common Mistakes and Solutions

### 1. Migration Issues
**Problem:** Forgetting to run migrations after model changes
**Solution:** Always run `makemigrations` and `migrate` after model changes

### 2. Template Not Found
**Problem:** Django can't find your templates
**Solution:** Check `TEMPLATES` setting and ensure correct directory structure

### 3. URL Reverse Errors
**Problem:** `{% url %}` tag fails to resolve
**Solution:** Ensure URL names match and include app namespace

### 4. Import Errors
**Problem:** Views can't import models
**Solution:** Use relative imports: `from .models import Book`

### 5. Context Data Missing
**Problem:** Template variables are empty
**Solution:** Ensure context dictionary includes all needed data

---

## Next Steps

After completing these exercises, you should understand:
- How Django's MTV pattern works
- The relationship between models, views, and templates
- How URL routing connects everything together
- The difference between function-based and class-based views
- Template inheritance and Django template language

**Continue Learning:**
1. Forms and form handling
2. User authentication and permissions
3. Django admin customization
4. Database relationships and queries
5. Static files and media handling

## Additional Challenges

### Challenge 1: Add Book Categories
Extend the Book model with a Category model and foreign key relationship.

### Challenge 2: Implement Book Reviews
Add a Review model with a foreign key to Book and display reviews on the detail page.

### Challenge 3: Add AJAX Search
Implement real-time search using JavaScript and Django's JSON responses.

### Challenge 4: Create a REST API
Use Django REST Framework to create API endpoints for your books.

These exercises provide hands-on experience with Django's core concepts and prepare you for building more complex applications!