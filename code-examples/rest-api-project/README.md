# Django REST API Project

This is a complete example of a Django REST API built with Django REST Framework. It demonstrates a blog API with posts, categories, comments, and user authentication.

## Features

- User authentication with token-based auth
- CRUD operations for blog posts and categories
- Comment system with nested replies
- User permissions and custom permission classes
- API filtering, searching, and pagination
- Comprehensive test suite
- API documentation with Swagger/OpenAPI
- Custom serializers and viewsets

## Project Structure

```
rest-api-project/
├── blog_api/                 # Main Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── blog/                     # Blog app
│   ├── models.py            # Post, Category, Comment models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # API viewsets
│   ├── permissions.py       # Custom permissions
│   ├── urls.py              # API URLs
│   └── tests.py             # API tests
├── requirements.txt
└── manage.py
```

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

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Create authentication tokens:
```bash
python manage.py create_tokens
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login and get token
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/register/` - Register new user

### Posts
- `GET /api/posts/` - List all posts (with filtering, search, pagination)
- `POST /api/posts/` - Create new post (authenticated)
- `GET /api/posts/{id}/` - Get specific post
- `PUT /api/posts/{id}/` - Update post (author only)
- `DELETE /api/posts/{id}/` - Delete post (author only)
- `POST /api/posts/{id}/publish/` - Publish post (author only)
- `GET /api/posts/published/` - Get only published posts
- `GET /api/posts/my_posts/` - Get current user's posts

### Categories
- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create category (authenticated)
- `GET /api/categories/{id}/` - Get specific category
- `PUT /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category

### Comments
- `GET /api/posts/{post_id}/comments/` - List post comments
- `POST /api/posts/{post_id}/comments/` - Add comment to post
- `PUT /api/comments/{id}/` - Update comment (author only)
- `DELETE /api/comments/{id}/` - Delete comment (author only)

## API Usage Examples

### Authentication
```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "user@example.com", "password": "securepass123"}'

# Login to get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "securepass123"}'
```

### Creating a Post
```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First API Post",
    "content": "This post was created via the API!",
    "category": 1,
    "published": true
  }'
```

### Filtering and Searching
```bash
# Search posts by title
curl "http://localhost:8000/api/posts/?search=django"

# Filter by category
curl "http://localhost:8000/api/posts/?category=1"

# Filter published posts only
curl "http://localhost:8000/api/posts/?published=true"

# Combine filters
curl "http://localhost:8000/api/posts/?category=1&published=true&search=tutorial"
```

## Testing

Run the test suite:
```bash
python manage.py test
```

Run with coverage:
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## API Documentation

Once the server is running, visit:
- Browsable API: http://localhost:8000/api/
- Swagger Documentation: http://localhost:8000/api/docs/
- OpenAPI Schema: http://localhost:8000/api/schema/

## Key Learning Points

This project demonstrates:

1. **Model Relationships**: Foreign keys and many-to-many relationships
2. **Serializer Patterns**: Different serializers for different actions
3. **ViewSet Customization**: Custom actions and method overrides
4. **Permission System**: Built-in and custom permissions
5. **Authentication**: Token-based authentication
6. **Filtering & Search**: Using django-filter and DRF filters
7. **Testing**: Comprehensive API testing with DRF test tools
8. **Documentation**: Auto-generated API documentation

## Common Issues and Solutions

### CORS Errors
If you're accessing the API from a frontend application, you may need to configure CORS:
```bash
pip install django-cors-headers
```

### Token Authentication
Make sure to include the token in the Authorization header:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Permission Denied
Check that:
- You're authenticated for protected endpoints
- You have the right permissions for the action
- You're the author of the resource for author-only actions

## Next Steps

To extend this project, consider adding:
- JWT authentication instead of token auth
- File upload capabilities for post images
- Email notifications for comments
- Rate limiting and throttling
- Caching with Redis
- Full-text search with Elasticsearch
- WebSocket support for real-time features