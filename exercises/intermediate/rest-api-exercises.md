# Django REST Framework Exercises

These exercises will help you practice building REST APIs with Django REST Framework. Each exercise builds upon the previous ones, so complete them in order.

## Prerequisites

- Completed Django basics tutorial
- Understanding of HTTP methods and REST principles
- Basic knowledge of JSON format
- Familiarity with Django models and views

## Exercise 1: Basic API Setup

### Objective
Set up a basic Django REST Framework project and create your first API endpoint.

### Tasks

1. **Create a new Django project called `library_api`**
   ```bash
   django-admin startproject library_api
   cd library_api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Django REST Framework**
   ```bash
   pip install djangorestframework
   pip install markdown
   pip install django-filter
   ```

3. **Create a `books` app**
   ```bash
   python manage.py startapp books
   ```

4. **Configure settings.py**
   - Add `rest_framework` and `books` to `INSTALLED_APPS`
   - Add basic REST framework configuration

5. **Create a simple Book model**
   ```python
   # books/models.py
   class Book(models.Model):
       title = models.CharField(max_length=200)
       author = models.CharField(max_length=100)
       isbn = models.CharField(max_length=13, unique=True)
       publication_date = models.DateField()
       pages = models.PositiveIntegerField()
       created_at = models.DateTimeField(auto_now_add=True)
   ```

6. **Create and run migrations**

7. **Create a basic serializer for the Book model**

8. **Create a simple API view that returns a list of books**

9. **Configure URLs to access your API at `/api/books/`**

10. **Test your API using the browsable API interface**

### Expected Output
- A working API endpoint that returns JSON data
- Ability to view the API in a browser
- Basic CRUD operations working

### Validation Criteria
- [ ] API returns proper JSON response
- [ ] Browsable API interface is accessible
- [ ] Can create, read, update, and delete books
- [ ] Proper HTTP status codes are returned

---

## Exercise 2: Serializers and Validation

### Objective
Learn to create custom serializers with validation and different serialization contexts.

### Tasks

1. **Extend the Book model**
   ```python
   class Book(models.Model):
       # ... existing fields
       description = models.TextField(blank=True)
       price = models.DecimalField(max_digits=10, decimal_places=2)
       available = models.BooleanField(default=True)
       genre = models.CharField(max_length=50)
   ```

2. **Create a detailed BookSerializer with custom validation**
   - Validate that publication_date is not in the future
   - Ensure price is positive
   - Validate ISBN format (13 digits)
   - Add custom validation for pages (minimum 10)

3. **Create a BookListSerializer for list views (minimal fields)**

4. **Add a method field to calculate book age**

5. **Create custom validation for the genre field**
   - Only allow specific genres: Fiction, Non-Fiction, Science, History, Biography

6. **Test validation by trying to create invalid books**

### Expected Output
- Proper validation errors for invalid data
- Different serialization for list vs detail views
- Custom calculated fields in API responses

### Validation Criteria
- [ ] Custom validation rules work correctly
- [ ] Appropriate error messages are returned
- [ ] List and detail serializers show different fields
- [ ] Method fields are calculated correctly

---

## Exercise 3: ViewSets and Advanced Views

### Objective
Implement ViewSets and add custom actions to your API.

### Tasks

1. **Convert your views to use ModelViewSet**

2. **Add filtering capabilities**
   - Filter by genre
   - Filter by availability
   - Filter by price range

3. **Add search functionality**
   - Search in title and author fields

4. **Implement custom actions**
   - `@action` for marking a book as unavailable
   - `@action` for getting books by a specific author
   - `@action` for getting featured books (top 10 by some criteria)

5. **Add pagination**
   - Configure page size to 10
   - Add custom pagination class with additional metadata

6. **Create a separate Author model and relationship**
   ```python
   class Author(models.Model):
       name = models.CharField(max_length=100)
       bio = models.TextField(blank=True)
       birth_date = models.DateField(null=True, blank=True)
       nationality = models.CharField(max_length=50, blank=True)
   
   # Update Book model
   class Book(models.Model):
       # ... other fields
       authors = models.ManyToManyField(Author, related_name='books')
   ```

7. **Create AuthorViewSet with nested book listings**

### Expected Output
- Full CRUD operations through ViewSets
- Working filtering and search
- Custom actions accessible via API
- Paginated responses
- Author-book relationships working

### Validation Criteria
- [ ] All CRUD operations work through ViewSets
- [ ] Filtering and search return correct results
- [ ] Custom actions are accessible and functional
- [ ] Pagination works correctly
- [ ] Author-book relationships are properly serialized

---

## Exercise 4: Authentication and Permissions

### Objective
Implement authentication and custom permissions for your API.

### Tasks

1. **Set up Token Authentication**
   - Add `rest_framework.authtoken` to INSTALLED_APPS
   - Run migrations
   - Create tokens for users

2. **Create user registration endpoint**
   - Allow users to register with username, email, and password
   - Return authentication token upon registration

3. **Create login endpoint**
   - Return token for valid credentials

4. **Implement custom permissions**
   - `IsAuthorOrReadOnly`: Only book authors can edit their books
   - `IsLibrarianOrReadOnly`: Only librarians can add/delete books
   - Create a `Librarian` group and assign permissions

5. **Add user ownership to books**
   - Add `added_by` field to Book model (ForeignKey to User)
   - Automatically set the user when creating books

6. **Create user profile endpoints**
   - Users can view and edit their own profiles
   - Include list of books they've added

7. **Add rate limiting**
   - Limit API calls per user
   - Different limits for authenticated vs anonymous users

### Expected Output
- Token-based authentication working
- User registration and login endpoints
- Custom permissions enforced
- User-specific data access

### Validation Criteria
- [ ] Users can register and receive tokens
- [ ] Authentication is required for write operations
- [ ] Custom permissions work correctly
- [ ] Users can only edit their own content
- [ ] Rate limiting is enforced

---

## Exercise 5: Testing and Documentation

### Objective
Write comprehensive tests for your API and create documentation.

### Tasks

1. **Write unit tests for models**
   - Test model validation
   - Test model methods and properties
   - Test model relationships

2. **Write API tests**
   - Test all CRUD operations
   - Test authentication and permissions
   - Test filtering and search
   - Test custom actions
   - Test error handling

3. **Create integration tests**
   - Test complete workflows (register → login → create book → update → delete)
   - Test user permissions across different scenarios

4. **Set up API documentation**
   - Install and configure `drf-spectacular`
   - Add docstrings to your views and serializers
   - Generate OpenAPI schema
   - Set up Swagger UI

5. **Add custom documentation**
   - Document your custom actions
   - Add examples for complex operations
   - Document authentication flow

6. **Create test data fixtures**
   - Create sample data for testing
   - Use Django fixtures or factory_boy

### Expected Output
- Comprehensive test suite with good coverage
- Automatic API documentation
- Clear examples and usage instructions

### Validation Criteria
- [ ] All tests pass
- [ ] Test coverage is above 90%
- [ ] API documentation is accessible and complete
- [ ] Examples work correctly
- [ ] Error scenarios are documented

---

## Exercise 6: Advanced Features

### Objective
Implement advanced API features like file uploads, caching, and performance optimization.

### Tasks

1. **Add file upload functionality**
   - Add `cover_image` field to Book model
   - Handle image uploads in API
   - Add image validation (size, format)
   - Create thumbnail generation

2. **Implement caching**
   - Cache book list responses
   - Cache individual book details
   - Implement cache invalidation on updates

3. **Add bulk operations**
   - Bulk create books from CSV
   - Bulk update book availability
   - Bulk delete operations

4. **Optimize database queries**
   - Use `select_related` and `prefetch_related`
   - Add database indexes
   - Optimize serializer queries

5. **Add API versioning**
   - Implement URL path versioning
   - Create v2 API with additional fields
   - Maintain backward compatibility

6. **Implement advanced filtering**
   - Date range filtering
   - Complex query combinations
   - Custom filter backends

7. **Add real-time features**
   - WebSocket notifications for new books
   - Real-time availability updates

### Expected Output
- File upload functionality working
- Improved API performance
- Bulk operations available
- Versioned API endpoints

### Validation Criteria
- [ ] File uploads work correctly with validation
- [ ] Caching improves response times
- [ ] Bulk operations handle large datasets
- [ ] Database queries are optimized
- [ ] API versioning works correctly

---

## Bonus Challenges

### Challenge 1: Library Management System
Extend your API to include:
- Book borrowing system
- Due date tracking
- Fine calculations
- Reservation system

### Challenge 2: Analytics API
Add analytics endpoints:
- Most popular books
- User activity statistics
- Genre popularity trends
- Monthly reports

### Challenge 3: External API Integration
Integrate with external services:
- Google Books API for book information
- Email notifications for due dates
- Payment processing for fines
- Social media sharing

### Challenge 4: Mobile API Optimization
Optimize for mobile clients:
- Minimal response payloads
- Offline synchronization
- Push notifications
- Image optimization

## Solutions and Hints

### Common Issues and Solutions

1. **CORS Errors**
   ```python
   # Install django-cors-headers
   pip install django-cors-headers
   
   # Add to MIDDLEWARE in settings.py
   'corsheaders.middleware.CorsMiddleware',
   ```

2. **Token Authentication Not Working**
   ```python
   # Make sure to include token in headers
   headers = {'Authorization': 'Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b'}
   ```

3. **Serializer Validation Errors**
   ```python
   def validate_field_name(self, value):
       if some_condition:
           raise serializers.ValidationError("Error message")
       return value
   ```

4. **Permission Denied Issues**
   ```python
   # Check permission classes and authentication
   permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
   ```

### Testing Tips

1. **Use APITestCase for API tests**
   ```python
   from rest_framework.test import APITestCase
   from rest_framework import status
   ```

2. **Create test data in setUp method**
   ```python
   def setUp(self):
       self.user = User.objects.create_user(username='test', password='test')
       self.book = Book.objects.create(...)
   ```

3. **Test authentication**
   ```python
   self.client.force_authenticate(user=self.user)
   ```

### Performance Tips

1. **Use select_related for ForeignKey**
   ```python
   queryset = Book.objects.select_related('author')
   ```

2. **Use prefetch_related for ManyToMany**
   ```python
   queryset = Book.objects.prefetch_related('authors')
   ```

3. **Add database indexes**
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['title']),
           models.Index(fields=['publication_date']),
       ]
   ```

## Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [REST API Best Practices](https://restfulapi.net/)

## Submission Guidelines

For each exercise, submit:
1. Complete source code
2. Requirements.txt file
3. README with setup instructions
4. Test results and coverage report
5. API documentation screenshots
6. Brief explanation of design decisions

Good luck with your Django REST Framework journey!