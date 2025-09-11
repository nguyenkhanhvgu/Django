# Django Blog Tutorial - Complete Source Code

This directory contains the complete source code for the Django blog tutorial, organized by commit points for incremental learning.

## Project Structure

```
blog-tutorial/
├── myblog/                 # Django project directory
│   ├── myblog/            # Project settings
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── blog/              # Blog application
│   │   ├── migrations/
│   │   ├── templates/
│   │   ├── static/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── manage.py
│   └── requirements.txt
└── commit-history.md      # Detailed commit history
```

## Setup Instructions

1. **Clone or download** this code example
2. **Navigate** to the myblog directory:
   ```bash
   cd blog-tutorial/myblog
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```
6. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```
7. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

## Commit Points

This code is organized to match the tutorial's commit points:

1. **Initial project setup** - Basic Django project structure
2. **Blog app creation** - Blog app added to INSTALLED_APPS
3. **Models creation** - Post and Comment models with migrations
4. **Admin interface** - Admin configuration for content management
5. **Views creation** - List and detail views with pagination
6. **Forms creation** - Comment form for user interaction
7. **URL configuration** - URL patterns for blog views
8. **Templates creation** - HTML templates with Bootstrap styling
9. **Complete functionality** - Working blog with comments
10. **Custom styling** - Enhanced CSS for better appearance

## Features Included

- ✅ Blog post creation and display
- ✅ Comment system with moderation
- ✅ Admin interface for content management
- ✅ Responsive design with Bootstrap
- ✅ Pagination for post lists
- ✅ SEO-friendly URLs
- ✅ Form validation and error handling

## Learning Objectives

By studying this code, you will understand:

- Django project and app structure
- Model relationships and database operations
- View functions and class-based views
- Template inheritance and context variables
- Form handling and validation
- URL routing and namespacing
- Admin interface customization
- Static file management

## Testing the Application

1. Access the admin at `http://127.0.0.1:8000/admin/`
2. Create some blog posts with "Published" status
3. View the blog at `http://127.0.0.1:8000/`
4. Click on posts to view details and add comments
5. Test pagination by creating more than 3 posts

## Troubleshooting

See the troubleshooting guide in the main tutorial documentation for common issues and solutions.