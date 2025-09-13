# Comprehensive Testing in Django

## Introduction

Testing is a critical aspect of Django development that ensures your application works correctly, maintains quality over time, and provides confidence when making changes. This comprehensive guide covers testing strategies, test-driven development (TDD), testing tools, and automated testing pipelines for Django applications.

## Table of Contents

1. [Testing Strategy Overview](#testing-strategy-overview)
2. [Types of Tests in Django](#types-of-tests-in-django)
3. [Test-Driven Development (TDD)](#test-driven-development-tdd)
4. [Django Testing Framework](#django-testing-framework)
5. [Testing Tools and Frameworks Comparison](#testing-tools-and-frameworks-comparison)
6. [Advanced Testing Techniques](#advanced-testing-techniques)
7. [Automated Testing Pipelines](#automated-testing-pipelines)
8. [Best Practices and Common Patterns](#best-practices-and-common-patterns)

## Testing Strategy Overview

A comprehensive testing strategy for Django applications should include multiple levels of testing:

### Testing Pyramid

```
    /\
   /  \
  / UI \     <- Few, expensive, slow
 /______\
/        \
| Integration | <- Some, moderate cost
|____________|
|            |
|    Unit     | <- Many, cheap, fast
|____________|
```

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test how components work together
3. **Functional Tests**: Test complete user workflows
4. **Performance Tests**: Test application performance under load
5. **Security Tests**: Test for common security vulnerabilities

## Types of Tests in Django

### 1. Unit Tests

Unit tests focus on testing individual components like models, views, forms, and utility functions in isolation.

#### Model Testing

```python
# tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from blog.models import Post, Category

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )

    def test_post_creation(self):
        """Test that a post can be created with valid data"""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='This is a test post content.',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.slug, 'test-post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.category, self.category)
        self.assertEqual(str(post), 'Test Post')

    def test_post_slug_uniqueness(self):
        """Test that post slugs must be unique"""
        Post.objects.create(
            title='First Post',
            slug='test-slug',
            content='First post content.',
            author=self.user,
            category=self.category
        )
        
        with self.assertRaises(ValidationError):
            duplicate_post = Post(
                title='Second Post',
                slug='test-slug',
                content='Second post content.',
                author=self.user,
                category=self.category
            )
            duplicate_post.full_clean()

    def test_post_str_representation(self):
        """Test the string representation of a post"""
        post = Post.objects.create(
            title='Test Post Title',
            slug='test-post-title',
            content='Test content',
            author=self.user,
            category=self.category
        )
        self.assertEqual(str(post), 'Test Post Title')

    def test_post_get_absolute_url(self):
        """Test the get_absolute_url method"""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            author=self.user,
            category=self.category
        )
        expected_url = f'/blog/{post.slug}/'
        self.assertEqual(post.get_absolute_url(), expected_url)
```

#### View Testing

```python
# tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import Http404
from blog.models import Post, Category
from blog.views import PostListView, PostDetailView

class PostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='This is a test post.',
            author=self.user,
            category=self.category,
            status='published'
        )

    def test_post_list_view(self):
        """Test the post list view returns correct posts"""
        url = reverse('blog:post_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertIn('posts', response.context)
        self.assertEqual(len(response.context['posts']), 1)

    def test_post_detail_view(self):
        """Test the post detail view displays correct post"""
        url = reverse('blog:post_detail', kwargs={'slug': self.post.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)
        self.assertEqual(response.context['post'], self.post)

    def test_post_detail_view_404(self):
        """Test that non-existent post returns 404"""
        url = reverse('blog:post_detail', kwargs={'slug': 'non-existent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_draft_post_not_visible(self):
        """Test that draft posts are not visible in public views"""
        draft_post = Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='This is a draft.',
            author=self.user,
            category=self.category,
            status='draft'
        )
        
        # Should not appear in list view
        list_url = reverse('blog:post_list')
        response = self.client.get(list_url)
        self.assertNotContains(response, draft_post.title)
        
        # Should return 404 for detail view
        detail_url = reverse('blog:post_detail', kwargs={'slug': draft_post.slug})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)
```

#### Form Testing

```python
# tests/test_forms.py
from django.test import TestCase
from django.contrib.auth.models import User
from blog.forms import PostForm, CommentForm
from blog.models import Category

class PostFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )

    def test_post_form_valid_data(self):
        """Test form with valid data"""
        form_data = {
            'title': 'Test Post',
            'content': 'This is test content.',
            'category': self.category.id,
            'tags': 'django, testing'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_form_missing_title(self):
        """Test form validation with missing title"""
        form_data = {
            'content': 'This is test content.',
            'category': self.category.id,
        }
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_post_form_save(self):
        """Test form save method"""
        form_data = {
            'title': 'Test Post',
            'content': 'This is test content.',
            'category': self.category.id,
            'tags': 'django, testing'
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        post = form.save(commit=False)
        post.author = self.user
        post.save()
        
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.category, self.category)
```

### 2. Integration Tests

Integration tests verify that different parts of your application work together correctly.

```python
# tests/test_integration.py
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.contrib.auth.models import User
from django.core import mail
from blog.models import Post, Category, Comment
from blog.services import PostService, NotificationService

class PostServiceIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )

    def test_post_creation_with_notifications(self):
        """Test that creating a post triggers notifications"""
        post_data = {
            'title': 'New Post',
            'content': 'This is a new post.',
            'category': self.category,
            'author': self.user
        }
        
        # Create post using service
        post = PostService.create_post(**post_data)
        
        # Verify post was created
        self.assertTrue(Post.objects.filter(title='New Post').exists())
        
        # Verify notification was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('New Post Published', mail.outbox[0].subject)

    def test_comment_moderation_workflow(self):
        """Test the complete comment moderation workflow"""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # Create comment
        comment = Comment.objects.create(
            post=post,
            author_name='Commenter',
            author_email='commenter@example.com',
            content='This is a test comment.',
            status='pending'
        )
        
        # Approve comment
        comment.approve()
        
        # Verify comment is approved and notification sent
        comment.refresh_from_db()
        self.assertEqual(comment.status, 'approved')
        self.assertEqual(len(mail.outbox), 1)
```

### 3. Functional Tests

Functional tests simulate real user interactions with your application.

```python
# tests/test_functional.py
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from blog.models import Post, Category

class BlogFunctionalTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()  # or webdriver.Firefox()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )

    def test_user_can_view_blog_posts(self):
        """Test that a user can view blog posts"""
        # Create a test post
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='This is a test post.',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # User visits the blog
        self.selenium.get(f'{self.live_server_url}/blog/')
        
        # User sees the post title
        self.assertIn('Test Post', self.selenium.page_source)
        
        # User clicks on the post
        post_link = self.selenium.find_element(By.LINK_TEXT, 'Test Post')
        post_link.click()
        
        # User sees the full post content
        self.assertIn('This is a test post.', self.selenium.page_source)

    def test_user_can_submit_comment(self):
        """Test that a user can submit a comment"""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='This is a test post.',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # User visits the post detail page
        self.selenium.get(f'{self.live_server_url}/blog/{post.slug}/')
        
        # User fills out comment form
        name_input = self.selenium.find_element(By.NAME, 'author_name')
        email_input = self.selenium.find_element(By.NAME, 'author_email')
        content_input = self.selenium.find_element(By.NAME, 'content')
        
        name_input.send_keys('Test Commenter')
        email_input.send_keys('commenter@example.com')
        content_input.send_keys('This is a test comment.')
        
        # User submits the form
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        submit_button.click()
        
        # User sees success message
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))
        )
        self.assertIn('Comment submitted', self.selenium.page_source)
```

## Test-Driven Development (TDD)

Test-Driven Development is a software development approach where you write tests before writing the actual code. The TDD cycle follows three steps:

1. **Red**: Write a failing test
2. **Green**: Write the minimum code to make the test pass
3. **Refactor**: Improve the code while keeping tests passing

### TDD Example: Building a Blog Post Model

Let's walk through building a blog post model using TDD:

#### Step 1: Write the First Test (Red)

```python
# tests/test_models.py
from django.test import TestCase
from blog.models import Post

class PostModelTest(TestCase):
    def test_post_creation(self):
        """Test that a post can be created"""
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post.'
        )
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.content, 'This is a test post.')
```

This test will fail because the `Post` model doesn't exist yet.

#### Step 2: Write Minimum Code (Green)

```python
# blog/models.py
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
```

Now the test passes, but we need more functionality.

#### Step 3: Add More Tests (Red)

```python
# tests/test_models.py
def test_post_str_representation(self):
    """Test the string representation of a post"""
    post = Post(title='Test Post')
    self.assertEqual(str(post), 'Test Post')

def test_post_slug_generation(self):
    """Test that slug is automatically generated from title"""
    post = Post.objects.create(
        title='Test Post Title',
        content='Test content'
    )
    self.assertEqual(post.slug, 'test-post-title')
```

#### Step 4: Implement Features (Green)

```python
# blog/models.py
from django.db import models
from django.utils.text import slugify

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
```

#### Step 5: Refactor and Add More Tests

Continue this cycle, adding tests for edge cases, validation, and additional features:

```python
def test_post_slug_uniqueness(self):
    """Test that duplicate slugs are handled"""
    Post.objects.create(title='Test Post', content='Content 1')
    post2 = Post.objects.create(title='Test Post', content='Content 2')
    self.assertNotEqual(post2.slug, 'test-post')

def test_post_published_manager(self):
    """Test custom manager for published posts"""
    Post.objects.create(title='Published', content='Content', status='published')
    Post.objects.create(title='Draft', content='Content', status='draft')
    
    published_posts = Post.published.all()
    self.assertEqual(published_posts.count(), 1)
    self.assertEqual(published_posts.first().title, 'Published')
```

### TDD for Views

```python
# tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post

class PostCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_post_create_requires_login(self):
        """Test that creating a post requires authentication"""
        url = reverse('blog:post_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_authenticated_user_can_access_create_form(self):
        """Test that authenticated users can access the create form"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('blog:post_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Post')

    def test_post_creation_via_form(self):
        """Test creating a post via the form"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('blog:post_create')
        
        form_data = {
            'title': 'New Post',
            'content': 'This is a new post content.'
        }
        response = self.client.post(url, form_data)
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Post should be created
        self.assertTrue(Post.objects.filter(title='New Post').exists())
        
        # Post should be associated with the user
        post = Post.objects.get(title='New Post')
        self.assertEqual(post.author, self.user)
```

## Testing Tools and Frameworks Comparison

### Django's Built-in Testing Framework

**Pros:**
- Integrated with Django
- Test database management
- Client for testing views
- Fixtures support
- Transaction handling

**Cons:**
- Limited assertion methods
- No parallel test execution by default
- Basic mocking capabilities

**Best for:** Standard Django applications, beginners

### pytest-django

**Pros:**
- More powerful assertions
- Fixtures and dependency injection
- Parallel test execution
- Better error reporting
- Plugin ecosystem

**Cons:**
- Additional dependency
- Learning curve for pytest syntax

**Installation:**
```bash
pip install pytest-django
```

**Configuration (pytest.ini):**
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = myproject.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = --tb=short --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

**Example pytest test:**
```python
# test_models.py
import pytest
from django.contrib.auth.models import User
from blog.models import Post, Category

@pytest.mark.django_db
def test_post_creation():
    user = User.objects.create_user(username='testuser')
    category = Category.objects.create(name='Tech', slug='tech')
    
    post = Post.objects.create(
        title='Test Post',
        content='Test content',
        author=user,
        category=category
    )
    
    assert post.title == 'Test Post'
    assert post.author == user

@pytest.fixture
def sample_post(db):
    user = User.objects.create_user(username='testuser')
    category = Category.objects.create(name='Tech', slug='tech')
    return Post.objects.create(
        title='Sample Post',
        content='Sample content',
        author=user,
        category=category
    )

def test_post_str_representation(sample_post):
    assert str(sample_post) == 'Sample Post'
```

### Factory Boy

**Purpose:** Generate test data efficiently

**Installation:**
```bash
pip install factory-boy
```

**Example:**
```python
# factories.py
import factory
from django.contrib.auth.models import User
from blog.models import Post, Category

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())

class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
    
    title = factory.Faker('sentence', nb_words=4)
    content = factory.Faker('text')
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    status = 'published'

# Usage in tests
def test_post_creation_with_factory():
    post = PostFactory()
    assert post.title
    assert post.author
    assert post.category
    
def test_multiple_posts():
    posts = PostFactory.create_batch(5)
    assert len(posts) == 5
```

### Coverage.py

**Purpose:** Measure test coverage

**Installation:**
```bash
pip install coverage
```

**Usage:**
```bash
# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

**Configuration (.coveragerc):**
```ini
[run]
source = .
omit = 
    */venv/*
    */migrations/*
    manage.py
    */settings/*
    */tests/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

### Comparison Table

| Tool | Purpose | Pros | Cons | Best For |
|------|---------|------|------|----------|
| Django TestCase | Basic testing | Built-in, simple | Limited features | Small projects |
| pytest-django | Advanced testing | Powerful, flexible | Learning curve | Large projects |
| Factory Boy | Test data | Realistic data | Setup overhead | Complex models |
| Coverage.py | Code coverage | Detailed reports | Can be misleading | Quality assurance |
| Selenium | Browser testing | Real user simulation | Slow, brittle | UI testing |
| Mock/unittest.mock | Mocking | Isolation | Complex setup | Unit testing |

## Advanced Testing Techniques

### Mocking and Patching

```python
# tests/test_services.py
from unittest.mock import patch, Mock
from django.test import TestCase
from blog.services import EmailService, PostService

class PostServiceTest(TestCase):
    @patch('blog.services.EmailService.send_notification')
    def test_post_creation_sends_email(self, mock_send_notification):
        """Test that creating a post sends an email notification"""
        mock_send_notification.return_value = True
        
        post_data = {
            'title': 'Test Post',
            'content': 'Test content',
            'author_id': 1
        }
        
        PostService.create_post(**post_data)
        
        # Verify email service was called
        mock_send_notification.assert_called_once()
        
    @patch('requests.get')
    def test_external_api_integration(self, mock_get):
        """Test integration with external API"""
        # Mock the external API response
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'success'}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = PostService.validate_with_external_api('test-content')
        
        self.assertTrue(result)
        mock_get.assert_called_once_with(
            'https://api.example.com/validate',
            params={'content': 'test-content'}
        )
```

### Database Testing Strategies

```python
# tests/test_database.py
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.test.utils import override_settings
from blog.models import Post

class DatabaseTest(TestCase):
    def test_database_constraints(self):
        """Test database-level constraints"""
        with self.assertRaises(IntegrityError):
            # This should fail due to unique constraint
            Post.objects.create(title='', content='Test')

class TransactionTest(TransactionTestCase):
    def test_transaction_rollback(self):
        """Test transaction rollback behavior"""
        try:
            with transaction.atomic():
                Post.objects.create(title='Test', content='Content')
                # Force an error to trigger rollback
                raise Exception('Forced error')
        except Exception:
            pass
        
        # Post should not exist due to rollback
        self.assertEqual(Post.objects.count(), 0)

@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class InMemoryDatabaseTest(TestCase):
    """Tests using in-memory database for speed"""
    def test_fast_database_operations(self):
        # These tests run faster with in-memory database
        posts = [Post(title=f'Post {i}', content='Content') 
                for i in range(1000)]
        Post.objects.bulk_create(posts)
        self.assertEqual(Post.objects.count(), 1000)
```

### Performance Testing

```python
# tests/test_performance.py
import time
from django.test import TestCase
from django.test.utils import override_settings
from django.core.cache import cache
from blog.models import Post
from blog.views import PostListView

class PerformanceTest(TestCase):
    def setUp(self):
        # Create test data
        self.posts = [
            Post(title=f'Post {i}', content=f'Content {i}')
            for i in range(100)
        ]
        Post.objects.bulk_create(self.posts)

    def test_post_list_performance(self):
        """Test that post list loads within acceptable time"""
        start_time = time.time()
        
        response = self.client.get('/blog/')
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 1.0)  # Should load in under 1 second

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_caching_improves_performance(self):
        """Test that caching improves response time"""
        # First request (no cache)
        start_time = time.time()
        response1 = self.client.get('/blog/')
        first_request_time = time.time() - start_time
        
        # Second request (with cache)
        start_time = time.time()
        response2 = self.client.get('/blog/')
        second_request_time = time.time() - start_time
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertLess(second_request_time, first_request_time)
```

## Automated Testing Pipelines

### GitHub Actions Configuration

Create `.github/workflows/django.yml`:

```yaml
name: Django CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
        django-version: [3.2, 4.0, 4.1, 4.2]
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install Django==${{ matrix.django-version }}
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run migrations
      run: |
        python manage.py migrate
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
    
    - name: Run tests
      run: |
        coverage run --source='.' manage.py test
        coverage xml
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: Run linting
      run: |
        flake8 .
        black --check .
        isort --check-only .
    
    - name: Run security checks
      run: |
        bandit -r . -x tests/
        safety check

  integration-tests:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install selenium
    
    - name: Set up Chrome
      uses: browser-actions/setup-chrome@latest
    
    - name: Run integration tests
      run: |
        python manage.py test tests.integration
      env:
        SELENIUM_BROWSER: chrome
        HEADLESS: true

  deploy:
    runs-on: ubuntu-latest
    needs: [test, integration-tests]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add your deployment commands here
```

### GitLab CI Configuration

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - integration
  - deploy

variables:
  POSTGRES_DB: test_db
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  POSTGRES_HOST_AUTH_METHOD: trust

services:
  - postgres:13
  - redis:6

before_script:
  - apt-get update -qy
  - apt-get install -y python3-dev python3-pip
  - pip install -r requirements.txt
  - pip install -r requirements-test.txt

test:
  stage: test
  script:
    - python manage.py migrate
    - coverage run --source='.' manage.py test
    - coverage report
    - coverage xml
  coverage: '/TOTAL.+ ([0-9]{1,3}%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

lint:
  stage: test
  script:
    - flake8 .
    - black --check .
    - isort --check-only .

security:
  stage: test
  script:
    - bandit -r . -x tests/
    - safety check

integration:
  stage: integration
  script:
    - python manage.py collectstatic --noinput
    - python manage.py test tests.integration
  only:
    - main
    - develop

deploy_staging:
  stage: deploy
  script:
    - echo "Deploying to staging"
    # Add deployment commands
  only:
    - develop

deploy_production:
  stage: deploy
  script:
    - echo "Deploying to production"
    # Add deployment commands
  only:
    - main
  when: manual
```

### Docker-based Testing

Create `docker-compose.test.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    command: python manage.py test
    volumes:
      - .:/code
    environment:
      - DEBUG=1
      - DATABASE_URL=postgres://postgres:postgres@db:5432/test_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

  redis:
    image: redis:6

  selenium:
    image: selenium/standalone-chrome:latest
    ports:
      - "4444:4444"
    environment:
      - HUB_HOST=selenium
```

Run tests with Docker:

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Run specific test suite
docker-compose -f docker-compose.test.yml run web python manage.py test tests.unit

# Run with coverage
docker-compose -f docker-compose.test.yml run web coverage run --source='.' manage.py test
```

### Pre-commit Hooks

Install pre-commit:

```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.11.4
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: local
    hooks:
      - id: django-test
        name: Django Tests
        entry: python manage.py test
        language: system
        pass_filenames: false
        always_run: true
```

Install hooks:

```bash
pre-commit install
```

## Best Practices and Common Patterns

### Test Organization

```
tests/
├── __init__.py
├── test_models.py
├── test_views.py
├── test_forms.py
├── test_utils.py
├── integration/
│   ├── __init__.py
│   ├── test_workflows.py
│   └── test_api_integration.py
├── functional/
│   ├── __init__.py
│   └── test_user_journeys.py
└── fixtures/
    ├── test_data.json
    └── sample_images/
```

### Test Data Management

```python
# tests/fixtures.py
from django.contrib.auth.models import User
from blog.models import Post, Category

class TestDataMixin:
    """Mixin to provide common test data"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data that doesn't change during tests"""
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        cls.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )

    def create_post(self, **kwargs):
        """Helper method to create posts with default values"""
        defaults = {
            'title': 'Test Post',
            'content': 'Test content',
            'author': self.user,
            'category': self.category,
            'status': 'published'
        }
        defaults.update(kwargs)
        return Post.objects.create(**defaults)

# Usage in tests
class PostModelTest(TestDataMixin, TestCase):
    def test_post_creation(self):
        post = self.create_post(title='Custom Title')
        self.assertEqual(post.title, 'Custom Title')
```

### Custom Test Assertions

```python
# tests/assertions.py
from django.test import TestCase

class CustomAssertionsMixin:
    """Custom assertions for Django tests"""
    
    def assertRedirectsToLogin(self, response, next_url=None):
        """Assert that response redirects to login page"""
        self.assertEqual(response.status_code, 302)
        if next_url:
            self.assertIn(f'next={next_url}', response.url)
        self.assertIn('/login/', response.url)
    
    def assertContainsForm(self, response, form_class):
        """Assert that response contains a specific form"""
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], form_class)
    
    def assertEmailSent(self, subject_contains=None, to_email=None):
        """Assert that an email was sent"""
        from django.core import mail
        self.assertGreater(len(mail.outbox), 0)
        
        if subject_contains:
            self.assertIn(subject_contains, mail.outbox[-1].subject)
        
        if to_email:
            self.assertIn(to_email, mail.outbox[-1].to)

# Usage
class PostViewTest(CustomAssertionsMixin, TestCase):
    def test_create_post_requires_login(self):
        response = self.client.get('/blog/create/')
        self.assertRedirectsToLogin(response, '/blog/create/')
```

### Test Performance Optimization

```python
# tests/test_optimization.py
from django.test import TestCase, override_settings
from django.test.utils import override_settings

class OptimizedTestCase(TestCase):
    """Base test case with performance optimizations"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Use faster password hasher for tests
        cls.password_hasher = override_settings(
            PASSWORD_HASHERS=[
                'django.contrib.auth.hashers.MD5PasswordHasher',
            ]
        )
        cls.password_hasher.__enter__()
    
    @classmethod
    def tearDownClass(cls):
        cls.password_hasher.__exit__(None, None, None)
        super().tearDownClass()

# Use bulk operations for test data
class BulkDataTest(TestCase):
    def setUp(self):
        # Create multiple objects efficiently
        users = [
            User(username=f'user{i}', email=f'user{i}@example.com')
            for i in range(100)
        ]
        User.objects.bulk_create(users)
        
        posts = [
            Post(title=f'Post {i}', content=f'Content {i}', author_id=1)
            for i in range(1000)
        ]
        Post.objects.bulk_create(posts)
```

### Testing Async Views (Django 4.1+)

```python
# tests/test_async_views.py
from django.test import TestCase
from django.test.client import AsyncClient
import asyncio

class AsyncViewTest(TestCase):
    async def test_async_post_list(self):
        """Test async post list view"""
        client = AsyncClient()
        response = await client.get('/blog/async/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Posts')

    def test_async_view_sync_wrapper(self):
        """Test async view using sync test method"""
        async def async_test():
            client = AsyncClient()
            response = await client.get('/blog/async/')
            return response
        
        response = asyncio.run(async_test())
        self.assertEqual(response.status_code, 200)
```

### Common Testing Patterns

#### Testing Middleware

```python
# tests/test_middleware.py
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from blog.middleware import UserActivityMiddleware

class MiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = UserActivityMiddleware(lambda request: None)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_middleware_updates_last_activity(self):
        """Test that middleware updates user's last activity"""
        request = self.factory.get('/')
        request.user = self.user
        
        # Process request through middleware
        self.middleware(request)
        
        # Check that last_activity was updated
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_activity)
```

#### Testing Management Commands

```python
# tests/test_commands.py
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO

class ManagementCommandTest(TestCase):
    def test_cleanup_command(self):
        """Test the cleanup management command"""
        # Create test data
        old_posts = [
            Post.objects.create(
                title=f'Old Post {i}',
                content='Content',
                created_at=timezone.now() - timedelta(days=365)
            )
            for i in range(5)
        ]
        
        # Capture command output
        out = StringIO()
        call_command('cleanup_old_posts', stdout=out)
        
        # Verify posts were deleted
        self.assertEqual(Post.objects.count(), 0)
        self.assertIn('Deleted 5 old posts', out.getvalue())

    def test_command_with_invalid_args(self):
        """Test command with invalid arguments"""
        with self.assertRaises(CommandError):
            call_command('cleanup_old_posts', '--days', 'invalid')
```

This comprehensive testing tutorial covers all the essential aspects of testing Django applications, from basic unit tests to advanced testing techniques and automated pipelines. The examples provide practical, real-world scenarios that developers can adapt to their own projects.