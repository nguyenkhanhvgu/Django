# Django Blog Tutorial - Hands-On Exercises

These exercises are designed to reinforce the concepts learned in the Django blog tutorial. Complete them in order to build your understanding of Django's core features.

## Exercise 1: Database Operations and Models

### Objective
Practice working with Django models, database queries, and the Django ORM.

### Tasks

1. **Model Enhancement**
   - Add a `category` field to the Post model (CharField with max_length=50)
   - Add a `tags` field to the Post model (CharField with max_length=200, blank=True)
   - Create and run migrations for these changes

2. **Database Queries**
   - Create a Django shell session (`python manage.py shell`)
   - Practice these ORM operations:
     ```python
     # Import the models
     from blog.models import Post, Comment
     from django.contrib.auth.models import User
     
     # Create a new post
     user = User.objects.get(username='your_username')
     post = Post.objects.create(
         title='My Second Post',
         slug='my-second-post',
         author=user,
         body='This is my second blog post.',
         status='published',
         category='Technology',
         tags='django, python, web development'
     )
     
     # Query posts by category
     tech_posts = Post.objects.filter(category='Technology')
     
     # Get posts with comments
     posts_with_comments = Post.objects.filter(comments__isnull=False).distinct()
     
     # Count comments per post
     from django.db.models import Count
     posts_with_comment_count = Post.objects.annotate(comment_count=Count('comments'))
     ```

3. **Custom Model Methods**
   - Add a method `get_comment_count()` to the Post model
   - Add a method `get_recent_comments()` to return the last 3 comments

### Expected Output
- Successfully modified Post model with new fields
- Ability to create and query posts using the Django ORM
- Custom methods working correctly

### Solution Hints
- Remember to run `makemigrations` and `migrate` after model changes
- Use `objects.filter()` for queries and `objects.annotate()` for aggregations
- Custom methods go inside the model class definition

---

## Exercise 2: Forms and User Input

### Objective
Practice creating and handling Django forms, including validation and error handling.

### Tasks

1. **Create a Contact Form**
   - Create a new file `blog/forms.py` (if not exists) or add to existing
   - Create a `ContactForm` class with fields: name, email, subject, message
   - Add custom validation to ensure the message is at least 10 characters long

2. **Create a Contact View**
   - Add a `contact` view function in `blog/views.py`
   - Handle both GET (display form) and POST (process form) requests
   - On successful form submission, display a success message
   - On form errors, redisplay the form with error messages

3. **Create Contact Template**
   - Create `blog/templates/blog/contact.html`
   - Display the contact form with proper Bootstrap styling
   - Show form errors if any
   - Include a success message area

4. **Add URL Pattern**
   - Add URL pattern for the contact view
   - Test the form functionality

### Code Templates

**ContactForm (blog/forms.py):**
```python
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        return message
```

### Expected Output
- Working contact form with validation
- Proper error handling and display
- Success message on form submission

---

## Exercise 3: Template Rendering and Template Tags

### Objective
Practice Django template system, template inheritance, and custom template features.

### Tasks

1. **Create a Custom Template Filter**
   - Create `blog/templatetags/__init__.py` (empty file)
   - Create `blog/templatetags/blog_extras.py`
   - Add a custom filter `markdown_to_html` that converts simple markdown to HTML
   - Register and use the filter in templates

2. **Enhance Templates with More Features**
   - Add a sidebar with recent posts (last 5 posts)
   - Add a "Popular Posts" section (posts with most comments)
   - Create breadcrumb navigation
   - Add social sharing buttons (static links)

3. **Create Template Includes**
   - Create `blog/templates/blog/includes/recent_posts.html`
   - Create `blog/templates/blog/includes/popular_posts.html`
   - Include these in your base template sidebar

### Code Templates

**Custom Template Filter (blog/templatetags/blog_extras.py):**
```python
from django import template
import re

register = template.Library()

@register.filter
def markdown_to_html(value):
    # Simple markdown conversion
    # Convert **bold** to <strong>bold</strong>
    value = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', value)
    # Convert *italic* to <em>italic</em>
    value = re.sub(r'\*(.*?)\*', r'<em>\1</em>', value)
    # Convert line breaks to <br>
    value = value.replace('\n', '<br>')
    return value
```

**Recent Posts Include (blog/templates/blog/includes/recent_posts.html):**
```html
<div class="card mb-3">
    <div class="card-header">
        <h6>Recent Posts</h6>
    </div>
    <div class="card-body">
        {% for post in recent_posts %}
            <div class="mb-2">
                <a href="{{ post.get_absolute_url }}" class="text-decoration-none">
                    {{ post.title }}
                </a>
                <small class="text-muted d-block">{{ post.publish|date:"M d, Y" }}</small>
            </div>
        {% empty %}
            <p class="text-muted">No recent posts.</p>
        {% endfor %}
    </div>
</div>
```

### Expected Output
- Custom template filter working correctly
- Enhanced sidebar with recent and popular posts
- Clean template organization with includes

---

## Exercise 4: Advanced Features

### Objective
Implement more advanced Django features to enhance the blog functionality.

### Tasks

1. **Add Search Functionality**
   - Create a search form in the sidebar
   - Add a search view that filters posts by title and content
   - Display search results with highlighting

2. **Implement Post Categories**
   - Create a Category model
   - Update Post model to use ForeignKey to Category
   - Create category list and detail views
   - Add category navigation to templates

3. **Add Post Sharing**
   - Create a share view that sends post via email
   - Add share buttons to post detail template
   - Implement basic email functionality (console backend for testing)

### Code Templates

**Search View:**
```python
def post_search(request):
    form = SearchForm()
    query = None
    results = []
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.objects.filter(
                Q(title__icontains=query) | Q(body__icontains=query),
                status='published'
            )
    
    return render(request, 'blog/post/search.html', {
        'form': form,
        'query': query,
        'results': results
    })
```

### Expected Output
- Working search functionality
- Category system with navigation
- Email sharing capability (console output for testing)

---

## Exercise 5: Testing Your Blog

### Objective
Write comprehensive tests for your blog application.

### Tasks

1. **Model Tests**
   - Test Post model creation and methods
   - Test Comment model relationships
   - Test model validation

2. **View Tests**
   - Test post list view
   - Test post detail view
   - Test comment form submission
   - Test search functionality

3. **Form Tests**
   - Test CommentForm validation
   - Test ContactForm validation
   - Test form rendering

### Code Template

**View Tests:**
```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post, Comment

class BlogViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            body='This is a test post.',
            status='published'
        )

    def test_post_list_view(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')

    def test_post_detail_view(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)
```

### Expected Output
- All tests passing
- Good test coverage for models, views, and forms
- Understanding of Django testing framework

---

## Bonus Challenges

### Challenge 1: Admin Customization
- Customize the admin interface with list filters, search fields, and custom actions
- Add inline editing for comments in the post admin
- Create custom admin views

### Challenge 2: Performance Optimization
- Add database indexes to improve query performance
- Implement caching for frequently accessed data
- Optimize database queries using select_related and prefetch_related

### Challenge 3: User Authentication
- Add user registration and login functionality
- Allow users to create their own posts
- Implement user profiles with avatars

## Submission Guidelines

For each exercise:
1. Complete all tasks in the specified order
2. Test your implementation thoroughly
3. Document any challenges you encountered
4. Note any additional features you implemented

## Getting Help

If you get stuck:
1. Review the main tutorial documentation
2. Check the Django documentation
3. Use the Django shell to test queries
4. Review the troubleshooting guide
5. Ask for help with specific error messages

Remember: The goal is to learn by doing. Don't be afraid to experiment and try different approaches!