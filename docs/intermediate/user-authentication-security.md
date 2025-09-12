# User Authentication and Security in Django

## Table of Contents
1. [Introduction to Django Authentication](#introduction)
2. [Django's Built-in Authentication System](#built-in-auth)
3. [User Models and Customization](#user-models)
4. [Permissions and Authorization](#permissions)
5. [Security Best Practices](#security-practices)
6. [Hands-on Project: User Registration and Login](#hands-on-project)
7. [Advanced Authentication Topics](#advanced-topics)
8. [Exercises](#exercises)

## Introduction to Django Authentication {#introduction}

Django provides a robust authentication system out of the box that handles user accounts, groups, permissions, and cookie-based user sessions. This tutorial will guide you through implementing secure user authentication and authorization in your Django applications.

### What You'll Learn
- How Django's authentication system works
- Creating custom user models
- Implementing user registration and login
- Managing permissions and groups
- Security best practices for Django applications
- Password management and security

### Prerequisites
- Completed Django basics tutorial
- Understanding of Django models, views, and templates
- Basic knowledge of HTML forms

## Django's Built-in Authentication System {#built-in-auth}

Django's authentication system handles both authentication (verifying who a user is) and authorization (determining what an authenticated user is allowed to do).

### Core Components

#### 1. User Model
Django provides a built-in `User` model with these fields:
- `username`: Required. 150 characters or fewer.
- `first_name`: Optional. 150 characters or fewer.
- `last_name`: Optional. 150 characters or fewer.
- `email`: Optional. Email address.
- `password`: Required. Hash of the password.
- `is_staff`: Boolean. Designates whether user can access admin site.
- `is_active`: Boolean. Designates whether user account is active.
- `is_superuser`: Boolean. Designates that user has all permissions.
- `last_login`: DateTime of user's last login.
- `date_joined`: DateTime when account was created.

#### 2. Authentication Views
Django provides several built-in views for common authentication tasks:
- `LoginView`: Handles user login
- `LogoutView`: Handles user logout
- `PasswordChangeView`: Allows users to change their password
- `PasswordResetView`: Initiates password reset process

### Basic Authentication Setup

Let's start with a simple authentication setup:

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',  # Authentication framework
    'django.contrib.contenttypes',  # Content type system
    'django.contrib.sessions',  # Session framework
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',  # Our custom app for authentication
]

# Login/logout redirect URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

#### Creating an Accounts App

```bash
python manage.py startapp accounts
```

```python
# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Login/Logout
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Registration
    path('register/', views.register, name='register'),
    
    # Password management
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html'
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
]
```

#### Basic Login Template

```html
<!-- accounts/templates/accounts/login.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        .form-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 3px;
        }
        .btn {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .error {
            color: red;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Login</h2>
        
        {% if form.errors %}
            <div class="error">
                {{ form.errors }}
            </div>
        {% endif %}
        
        <form method="post">
            {% csrf_token %}
            <div class="form-group">
                <label for="{{ form.username.id_for_label }}">Username:</label>
                {{ form.username }}
            </div>
            
            <div class="form-group">
                <label for="{{ form.password.id_for_label }}">Password:</label>
                {{ form.password }}
            </div>
            
            <button type="submit" class="btn">Login</button>
        </form>
        
        <p><a href="{% url 'accounts:register' %}">Don't have an account? Register here</a></p>
    </div>
</body>
</html>
```

## User Models and Customization {#user-models}

While Django's built-in User model works for many applications, you often need to customize it for specific requirements.

### Extending the User Model

There are four ways to extend Django's User model:

#### 1. Proxy Model (for adding methods only)

```python
# accounts/models.py
from django.contrib.auth.models import User
from django.db import models

class UserProxy(User):
    class Meta:
        proxy = True
    
    def get_full_name_display(self):
        """Return full name or username if names are empty"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
    
    def get_user_type(self):
        """Determine user type based on permissions"""
        if self.is_superuser:
            return "Administrator"
        elif self.is_staff:
            return "Staff"
        else:
            return "Regular User"
```

#### 2. One-to-One Link (Profile Model)

```python
# accounts/models.py
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    website = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Automatically create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
```

#### 3. Custom User Model (Recommended for new projects)

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Use email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
```

```python
# settings.py
AUTH_USER_MODEL = 'accounts.CustomUser'
```

#### 4. Completely Custom User Model

```python
# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email
```

## Permissions and Authorization {#permissions}

Django's permission system allows you to control what users can and cannot do in your application.

### Built-in Permissions

Django automatically creates permissions for each model:
- `add_<modelname>`: Can add instances of the model
- `change_<modelname>`: Can change instances of the model  
- `delete_<modelname>`: Can delete instances of the model
- `view_<modelname>`: Can view instances of the model

### Custom Permissions

```python
# accounts/models.py
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        permissions = [
            ("can_publish", "Can publish blog posts"),
            ("can_feature", "Can feature blog posts"),
            ("can_moderate", "Can moderate comments"),
        ]
```

### Using Permissions in Views

```python
# accounts/views.py
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView
from django.shortcuts import render
from django.http import HttpResponseForbidden

# Function-based view with decorators
@login_required
@permission_required('accounts.can_publish', raise_exception=True)
def publish_post(request):
    # Only users with 'can_publish' permission can access this view
    return render(request, 'accounts/publish_post.html')

# Class-based view with mixins
class CreatePostView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = BlogPost
    fields = ['title', 'content']
    permission_required = 'accounts.add_blogpost'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

# Manual permission checking
def manual_permission_check(request):
    if not request.user.has_perm('accounts.can_moderate'):
        return HttpResponseForbidden("You don't have permission to moderate.")
    return render(request, 'accounts/moderate.html')
```

### Groups and Permissions

```python
# accounts/management/commands/setup_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from accounts.models import BlogPost

class Command(BaseCommand):
    help = 'Create user groups with specific permissions'
    
    def handle(self, *args, **options):
        # Create groups
        editors_group, created = Group.objects.get_or_create(name='Editors')
        moderators_group, created = Group.objects.get_or_create(name='Moderators')
        authors_group, created = Group.objects.get_or_create(name='Authors')
        
        # Get content type for BlogPost
        content_type = ContentType.objects.get_for_model(BlogPost)
        
        # Get permissions
        can_publish = Permission.objects.get(codename='can_publish', content_type=content_type)
        can_feature = Permission.objects.get(codename='can_feature', content_type=content_type)
        can_moderate = Permission.objects.get(codename='can_moderate', content_type=content_type)
        add_post = Permission.objects.get(codename='add_blogpost', content_type=content_type)
        change_post = Permission.objects.get(codename='change_blogpost', content_type=content_type)
        
        # Assign permissions to groups
        authors_group.permissions.set([add_post])
        editors_group.permissions.set([add_post, change_post, can_publish])
        moderators_group.permissions.set([add_post, change_post, can_publish, can_feature, can_moderate])
        
        self.stdout.write(self.style.SUCCESS('Successfully created groups and permissions'))
```

Run the command:
```bash
python manage.py setup_groups
```

### Assigning Users to Groups

```python
# In views or management commands
from django.contrib.auth.models import Group

def assign_user_to_group(user, group_name):
    group = Group.objects.get(name=group_name)
    user.groups.add(group)

# Example usage
user = User.objects.get(username='john_doe')
assign_user_to_group(user, 'Authors')
```
## S
ecurity Best Practices {#security-practices}

Security should be a primary concern when implementing authentication. Here are essential security practices for Django applications.

### 1. Password Security

#### Strong Password Requirements

```python
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Increase minimum length
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom password validator
class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one digit.")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
            raise ValidationError("Password must contain at least one special character.")
    
    def get_help_text(self):
        return "Password must contain uppercase, lowercase, digit, and special character."
```

#### Password Hashing Configuration

```python
# settings.py
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Most secure
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

### 2. Session Security

```python
# settings.py

# Session security settings
SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookies
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_COOKIE_AGE = 3600  # Session timeout (1 hour)

# CSRF protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 3. Rate Limiting and Brute Force Protection

```python
# accounts/decorators.py
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests
from django.conf import settings
import time

def rate_limit(max_requests=5, window=300, block_time=900):
    """
    Rate limiting decorator
    max_requests: Maximum requests allowed
    window: Time window in seconds
    block_time: Block time in seconds after limit exceeded
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get client IP
            ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                request.META.get('REMOTE_ADDR', ''))
            if ',' in ip:
                ip = ip.split(',')[0].strip()
            
            # Create cache keys
            attempts_key = f"login_attempts_{ip}"
            blocked_key = f"login_blocked_{ip}"
            
            # Check if IP is currently blocked
            if cache.get(blocked_key):
                return HttpResponseTooManyRequests(
                    "Too many failed attempts. Please try again later."
                )
            
            # Get current attempts
            attempts = cache.get(attempts_key, 0)
            
            # If this is a POST request (login attempt)
            if request.method == 'POST':
                # Check if limit exceeded
                if attempts >= max_requests:
                    cache.set(blocked_key, True, block_time)
                    cache.delete(attempts_key)
                    return HttpResponseTooManyRequests(
                        "Too many failed attempts. Account temporarily blocked."
                    )
                
                # Execute the view
                response = view_func(request, *args, **kwargs)
                
                # If login failed (assuming redirect means success)
                if response.status_code != 302:
                    cache.set(attempts_key, attempts + 1, window)
                else:
                    # Login successful, clear attempts
                    cache.delete(attempts_key)
                
                return response
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### 4. Two-Factor Authentication (2FA)

```python
# accounts/models.py
import pyotp
from django.db import models
from django.contrib.auth.models import User

class UserTwoFactor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret_key = models.CharField(max_length=32, blank=True)
    is_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    
    def generate_secret_key(self):
        """Generate a new secret key for TOTP"""
        self.secret_key = pyotp.random_base32()
        self.save()
        return self.secret_key
    
    def get_qr_code_url(self):
        """Generate QR code URL for authenticator apps"""
        if not self.secret_key:
            self.generate_secret_key()
        
        totp = pyotp.TOTP(self.secret_key)
        return totp.provisioning_uri(
            name=self.user.email,
            issuer_name="Your App Name"
        )
    
    def verify_token(self, token):
        """Verify TOTP token"""
        if not self.secret_key:
            return False
        
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self):
        """Generate backup codes for 2FA recovery"""
        import secrets
        codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.backup_codes = codes
        self.save()
        return codes
```

### 5. Input Validation and Sanitization

```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class SecureRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
    
    def clean_username(self):
        username = self.cleaned_data['username']
        
        # Only allow alphanumeric and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores.")
        
        # Check for reserved usernames
        reserved_usernames = ['admin', 'root', 'administrator', 'moderator']
        if username.lower() in reserved_usernames:
            raise ValidationError("This username is reserved.")
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        
        return email
    
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        
        # Only allow letters and spaces
        if not re.match(r'^[a-zA-Z\s]+$', first_name):
            raise ValidationError("First name can only contain letters and spaces.")
        
        return first_name.strip().title()
    
    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        
        # Only allow letters and spaces
        if not re.match(r'^[a-zA-Z\s]+$', last_name):
            raise ValidationError("Last name can only contain letters and spaces.")
        
        return last_name.strip().title()
```

### 6. Logging and Monitoring

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

# accounts/views.py
import logging
from django.contrib.auth import login, authenticate
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

security_logger = logging.getLogger('security')

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                         request.META.get('REMOTE_ADDR', 'Unknown'))
    username = credentials.get('username', 'Unknown')
    
    security_logger.warning(
        f"Failed login attempt for username '{username}' from IP {ip}"
    )
```

## Hands-on Project: User Registration and Login {#hands-on-project}

Let's build a complete user authentication system with registration, login, logout, and profile management.

### Project Structure

```
authentication_project/
├── manage.py
├── authentication_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│   │   └── accounts/
│   │       ├── base.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── profile.html
│   │       └── dashboard.html
│   └── static/
│       └── accounts/
│           └── style.css
└── requirements.txt
```

### Step 1: Project Setup

Create a new Django project:

```bash
django-admin startproject authentication_project
cd authentication_project
python manage.py startapp accounts
```

### Step 2: Models

```python
# accounts/models.py
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_pics')
    phone_number = models.CharField(max_length=15, blank=True)
    website = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image
        img = Image.open(self.avatar.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.avatar.path)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.userprofile.save()
```

### Step 3: Forms

```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'birth_date', 'avatar', 'phone_number', 'website']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if field_name != 'avatar':
                field.widget.attrs['class'] = 'form-control'
```

### Step 4: Views

```python
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            
            # Log the user in automatically
            user = authenticate(username=user.username, 
                              password=form.cleaned_data.get('password1'))
            if user is not None:
                login(request, user)
                return redirect('accounts:dashboard')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, 
                                 instance=request.user.userprofile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('accounts:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.userprofile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    
    return render(request, 'accounts/profile.html', context)
```

### Step 5: Templates

Base template:

```html
<!-- accounts/templates/accounts/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Authentication System{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .profile-img {
            height: 40px;
            width: 40px;
            border-radius: 50%;
            object-fit: cover;
        }
        .avatar-large {
            height: 150px;
            width: 150px;
            border-radius: 50%;
            object-fit: cover;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'accounts:dashboard' %}">AuthSystem</a>
            
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <a class="nav-link" href="{% url 'accounts:dashboard' %}">Dashboard</a>
                    <a class="nav-link" href="{% url 'accounts:profile' %}">Profile</a>
                    <a class="nav-link" href="{% url 'accounts:logout' %}">Logout</a>
                    <span class="navbar-text">
                        <img src="{{ user.userprofile.avatar.url }}" class="profile-img" alt="Avatar">
                        {{ user.username }}
                    </span>
                {% else %}
                    <a class="nav-link" href="{% url 'accounts:login' %}">Login</a>
                    <a class="nav-link" href="{% url 'accounts:register' %}">Register</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

Registration template:

```html
<!-- accounts/templates/accounts/register.html -->
{% extends 'accounts/base.html' %}

{% block title %}Register - Authentication System{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3 class="text-center">Create Account</h3>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    
                    <div class="mb-3">
                        <label for="{{ form.username.id_for_label }}" class="form-label">Username</label>
                        {{ form.username }}
                        {% if form.username.errors %}
                            <div class="text-danger">{{ form.username.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.email.id_for_label }}" class="form-label">Email</label>
                        {{ form.email }}
                        {% if form.email.errors %}
                            <div class="text-danger">{{ form.email.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="{{ form.first_name.id_for_label }}" class="form-label">First Name</label>
                            {{ form.first_name }}
                            {% if form.first_name.errors %}
                                <div class="text-danger">{{ form.first_name.errors }}</div>
                            {% endif %}
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="{{ form.last_name.id_for_label }}" class="form-label">Last Name</label>
                            {{ form.last_name }}
                            {% if form.last_name.errors %}
                                <div class="text-danger">{{ form.last_name.errors }}</div>
                            {% endif %}
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.password1.id_for_label }}" class="form-label">Password</label>
                        {{ form.password1 }}
                        {% if form.password1.errors %}
                            <div class="text-danger">{{ form.password1.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="{{ form.password2.id_for_label }}" class="form-label">Confirm Password</label>
                        {{ form.password2 }}
                        {% if form.password2.errors %}
                            <div class="text-danger">{{ form.password2.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100">Create Account</button>
                </form>
                
                <div class="text-center mt-3">
                    <p>Already have an account? <a href="{% url 'accounts:login' %}">Login here</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

Dashboard template:

```html
<!-- accounts/templates/accounts/dashboard.html -->
{% extends 'accounts/base.html' %}

{% block title %}Dashboard - Authentication System{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h4>Welcome, {{ user.get_full_name|default:user.username }}!</h4>
            </div>
            <div class="card-body">
                <p>This is your dashboard. Here you can:</p>
                <ul>
                    <li>View your account information</li>
                    <li>Update your profile</li>
                    <li>Change your password</li>
                    <li>Manage your account settings</li>
                </ul>
                
                <div class="mt-4">
                    <a href="{% url 'accounts:profile' %}" class="btn btn-primary">Edit Profile</a>
                    <a href="{% url 'password_change' %}" class="btn btn-secondary">Change Password</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5>Account Info</h5>
            </div>
            <div class="card-body text-center">
                <img src="{{ user.userprofile.avatar.url }}" class="avatar-large mb-3" alt="Avatar">
                <h6>{{ user.get_full_name|default:user.username }}</h6>
                <p class="text-muted">{{ user.email }}</p>
                <p><small>Member since {{ user.date_joined|date:"F Y" }}</small></p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Step 6: URL Configuration

```python
# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # User dashboard and profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Password management
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html'
    ), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),
    
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]
```

### Step 7: Settings Configuration

```python
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
]

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Login/logout redirects
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Email configuration (for password reset)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development
```

### Step 8: Running the Project

```bash
# Install dependencies
pip install Django Pillow

# Create and run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Advanced Authentication Topics {#advanced-topics}

### 1. Social Authentication

Using `django-allauth` for social login:

```bash
pip install django-allauth
```

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Social auth settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}
```

### 2. JWT Authentication for APIs

```python
# Using djangorestframework-simplejwt
pip install djangorestframework-simplejwt

# settings.py
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

### 3. Custom Authentication Backend

```python
# accounts/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailOrUsernameModelBackend(BaseBackend):
    """
    Custom authentication backend that allows login with email or username
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by email or username
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False
        """
        return getattr(user, 'is_active', None)
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

# settings.py
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```## Ex
ercises {#exercises}

### Exercise 1: Basic Authentication Setup

**Objective**: Set up a basic authentication system with login and logout functionality.

**Tasks**:
1. Create a new Django project called `auth_practice`
2. Create an `accounts` app
3. Implement login and logout views using Django's built-in views
4. Create templates for login and a simple dashboard
5. Add navigation links for authenticated and anonymous users

**Expected Outcome**: Users can log in and out, with appropriate redirects and navigation.

### Exercise 2: User Registration

**Objective**: Add user registration functionality to your authentication system.

**Tasks**:
1. Create a custom registration form that includes email validation
2. Implement a registration view that creates new users
3. Add email uniqueness validation
4. Create a registration template with proper error handling
5. Automatically log in users after successful registration

**Expected Outcome**: New users can register accounts and are automatically logged in.

### Exercise 3: User Profile Management

**Objective**: Extend the User model with a profile and allow users to update their information.

**Tasks**:
1. Create a `UserProfile` model with additional fields (bio, avatar, phone)
2. Create forms for updating user information and profile data
3. Implement a profile view that handles both user and profile updates
4. Add image upload functionality for avatars with size validation
5. Create a profile template that displays and allows editing of user data

**Expected Outcome**: Users can view and update their profile information including uploading avatars.

### Exercise 4: Permission-Based Access Control

**Objective**: Implement a permission system for different user roles.

**Tasks**:
1. Create a simple blog model with posts
2. Define custom permissions for publishing and moderating posts
3. Create user groups (Authors, Editors, Moderators) with different permissions
4. Implement views that check permissions before allowing actions
5. Create a management command to set up groups and permissions

**Expected Outcome**: Different user types have different capabilities based on their permissions.

### Exercise 5: Security Enhancements

**Objective**: Add security features to protect against common attacks.

**Tasks**:
1. Implement rate limiting for login attempts
2. Add strong password validation requirements
3. Configure secure session and CSRF settings
4. Add logging for security events (failed logins, permission denials)
5. Implement account lockout after multiple failed attempts

**Expected Outcome**: The application is protected against brute force attacks and has proper security logging.

### Exercise 6: Two-Factor Authentication

**Objective**: Add 2FA support to enhance account security.

**Tasks**:
1. Install and configure `pyotp` for TOTP generation
2. Create a model to store 2FA secrets and backup codes
3. Implement 2FA setup views with QR code generation
4. Add 2FA verification to the login process
5. Create backup code generation and recovery system

**Expected Outcome**: Users can enable 2FA and use authenticator apps to log in securely.

### Exercise Solutions

#### Exercise 1 Solution

```python
# accounts/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    context = {
        'user': request.user,
        'title': 'Dashboard'
    }
    return render(request, 'accounts/dashboard.html', context)

# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
```

#### Exercise 2 Solution

```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after registration
            return redirect('accounts:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
```

#### Exercise 3 Solution

```python
# accounts/models.py
from django.contrib.auth.models import User
from django.db import models
from PIL import Image

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_pics')
    phone = models.CharField(max_length=15, blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize avatar
        img = Image.open(self.avatar.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.avatar.path)

# accounts/forms.py
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'phone']
```

## Summary

This tutorial covered Django's comprehensive authentication system, including:

1. **Built-in Authentication**: Understanding Django's user model and authentication views
2. **Custom User Models**: Different approaches to extending user functionality
3. **Permissions and Authorization**: Implementing role-based access control
4. **Security Best Practices**: Protecting against common security threats
5. **Hands-on Project**: Building a complete authentication system
6. **Advanced Topics**: Social auth, JWT, and custom backends

### Key Takeaways

- Always use Django's built-in authentication system as a foundation
- Implement proper password policies and security measures
- Use permissions and groups for role-based access control
- Log security events for monitoring and debugging
- Consider 2FA for sensitive applications
- Keep security dependencies updated

### Next Steps

- Explore Django REST Framework for API authentication
- Learn about OAuth2 and OpenID Connect
- Study advanced security topics like SAML and SSO
- Practice implementing custom authentication flows
- Learn about security testing and penetration testing

### Additional Resources

- [Django Authentication Documentation](https://docs.djangoproject.com/en/stable/topics/auth/)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)
- [Two-Factor Authentication with Django](https://django-otp.readthedocs.io/)