# Django REST Framework Exercises

These exercises will help you practice the concepts covered in the Django REST Framework tutorial. Work through them in order, as each builds upon the previous ones.

## Exercise 1: Basic API Setup

**Objective**: Set up a basic Django REST Framework project with a simple model and API.

**Tasks**:
1. Create a new Django project called `library_api`
2. Install Django REST Framework and configure it in settings
3. Create a `books` app with a `Book` model containing:
   - `title` (CharField, max_length=200)
   - `author` (CharField, max_length=100)
   - `isbn` (CharField, max_length=13, unique=True)
   - `publication_date` (DateField)
   - `pages` (PositiveIntegerField)
   - `created_at` (DateTimeField, auto_now_add=True)

4. Create a basic serializer for the Book model
5. Create a simple API view to list and create books
6. Configure URLs and test your API

**Expected Result**: You should be able to GET and POST to `/api/books/` endpoint.

**Validation**: 
- GET request returns list of books
- POST request creates a new book
- Invalid data returns appropriate error messages

---

## Exercise 2: Advanced Serializers

**Objective**: Practice creating complex serializers with validation and custom fields.

**Tasks**:
1. Extend your Book model to include:
   - `genre` (CharField with choices: Fiction, Non-Fiction, Science, History, Biography)
   - `price` (DecimalField, max_digits=6, decimal_places=2)
   - `is_available` (BooleanField, default=True)

2. Create an advanced serializer that includes:
   - A custom field `age_in_days` that calculates days since publication
   - A `SerializerMethodField` for `reading_difficulty` based on page count
   - Custom validation to ensure price is positive
   - Custom validation to ensure publication_date is not in the future

3. Create separate serializers for list view (minimal fields) and detail view (all fields)

**Expected Result**: Your API should return calculated fields and validate input properly.

**Validation**:
- List view shows only essential fields
- Detail view shows all fields including calculated ones
- Invalid data (negative price, future date) is rejected

---

## Exercise 3: ViewSets and Custom Actions

**Objective**: Implement ViewSets with custom actions and filtering.

**Tasks**:
1. Convert your API views to use `ModelViewSet`
2. Add filtering capabilities:
   - Filter by genre
   - Filter by availability
   - Search by title and author
   - Order by publication_date and price

3. Implement custom actions:
   - `available_books` - returns only available books
   - `by_genre/{genre}` - returns books of specific genre
   - `mark_unavailable` - marks a book as unavailable (detail action)
   - `price_range` - accepts min/max price parameters

4. Add pagination with page size of 10

**Expected Result**: Your API should support filtering, searching, and custom actions.

**Validation**:
- Filtering works correctly
- Custom actions return expected results
- Pagination works properly

---

## Exercise 4: Authentication and Permissions

**Objective**: Implement authentication and permission system.

**Tasks**:
1. Add token authentication to your project
2. Create a custom permission class `IsLibrarianOrReadOnly` that:
   - Allows read access to everyone
   - Allows write access only to users with `is_staff=True`

3. Implement user registration and login endpoints
4. Add user model relationship to Book (who added the book)
5. Create a permission that allows users to edit only books they added

6. Add throttling:
   - Anonymous users: 100 requests per day
   - Authenticated users: 1000 requests per day

**Expected Result**: API should require authentication for modifications and respect permissions.

**Validation**:
- Anonymous users can read but not write
- Only staff users can add books
- Users can only edit their own books
- Throttling limits are enforced

---

## Exercise 5: Nested Resources and Relationships

**Objective**: Work with related models and nested serialization.

**Tasks**:
1. Create an `Author` model with:
   - `name` (CharField)
   - `bio` (TextField)
   - `birth_date` (DateField)
   - `nationality` (CharField)

2. Create a `Review` model with:
   - `book` (ForeignKey to Book)
   - `reviewer` (ForeignKey to User)
   - `rating` (IntegerField, 1-5)
   - `comment` (TextField)
   - `created_at` (DateTimeField)

3. Update Book model to use ForeignKey to Author instead of CharField
4. Create nested serializers that show:
   - Author details in book serialization
   - Book reviews in book detail view
   - Average rating calculation

5. Implement nested routes:
   - `/api/books/{id}/reviews/` - list/create reviews for a book
   - `/api/authors/{id}/books/` - list books by an author

**Expected Result**: API should handle complex relationships and nested data.

**Validation**:
- Book serialization includes author details
- Reviews are properly nested under books
- Average ratings are calculated correctly

---

## Exercise 6: Testing Your API

**Objective**: Write comprehensive tests for your API.

**Tasks**:
1. Create test cases for:
   - Book CRUD operations
   - Authentication flows
   - Permission checks
   - Custom actions
   - Validation errors

2. Test different user roles:
   - Anonymous users
   - Regular authenticated users
   - Staff users

3. Test edge cases:
   - Invalid data
   - Non-existent resources
   - Permission violations

4. Achieve at least 90% test coverage

**Expected Result**: Comprehensive test suite that validates all API functionality.

**Validation**:
- All tests pass
- High test coverage
- Edge cases are handled properly

---

## Exercise 7: API Documentation and Optimization

**Objective**: Document your API and optimize performance.

**Tasks**:
1. Install and configure `drf-spectacular` for OpenAPI documentation
2. Add proper docstrings and schema descriptions to your views
3. Optimize database queries:
   - Use `select_related` for foreign keys
   - Use `prefetch_related` for many-to-many relationships
   - Add database indexes where appropriate

4. Implement caching for frequently accessed endpoints
5. Add API versioning (v1, v2)
6. Create a simple frontend that consumes your API

**Expected Result**: Well-documented, optimized API with versioning.

**Validation**:
- Swagger documentation is accessible and complete
- Database queries are optimized
- API versioning works correctly

---

## Bonus Challenges

### Challenge 1: File Uploads
Add book cover image upload functionality with image validation and resizing.

### Challenge 2: Real-time Features
Implement WebSocket support for real-time book availability updates.

### Challenge 3: Advanced Search
Implement full-text search using PostgreSQL or Elasticsearch.

### Challenge 4: Rate Limiting
Implement sophisticated rate limiting based on user tiers.

### Challenge 5: API Analytics
Add endpoint usage analytics and monitoring.

---

## Solutions and Hints

### Exercise 1 Hints:
- Use `python manage.py startproject library_api`
- Don't forget to add `rest_framework` to `INSTALLED_APPS`
- Use `ModelSerializer` for quick setup
- Test with tools like Postman or curl

### Exercise 2 Hints:
- Use `SerializerMethodField` for calculated fields
- Override `validate_<field_name>` methods for custom validation
- Consider using `to_representation` for complex formatting

### Exercise 3 Hints:
- Use `@action(detail=False)` for collection actions
- Use `@action(detail=True)` for instance actions
- Configure `filter_backends` in your ViewSet
- Use `django-filter` for complex filtering

### Exercise 4 Hints:
- Add `rest_framework.authtoken` to `INSTALLED_APPS`
- Use `@permission_classes` decorator for custom permissions
- Configure throttling in `REST_FRAMEWORK` settings
- Create management command for token creation

### Exercise 5 Hints:
- Use `depth` parameter for simple nested serialization
- Create separate serializers for nested relationships
- Use `SerializerMethodField` for calculated fields like averages
- Consider using `prefetch_related` for performance

### Exercise 6 Hints:
- Use `APITestCase` from DRF
- Create test fixtures with `setUp` method
- Use `self.client.force_authenticate(user)` for auth tests
- Test both success and failure scenarios

### Exercise 7 Hints:
- Use `@extend_schema` decorator for documentation
- Configure caching with Redis or Memcached
- Use URL namespacing for versioning
- Consider using Django's cache framework

---

## Common Troubleshooting

### CORS Issues
If testing from a frontend, install `django-cors-headers`:
```bash
pip install django-cors-headers
```

### Authentication Problems
- Ensure token format: `Authorization: Token <your-token>`
- Check that `rest_framework.authtoken` is in `INSTALLED_APPS`
- Run migrations after adding token authentication

### Serialization Errors
- Check field names match model fields
- Validate required fields are provided
- Use `serializer.is_valid()` before `serializer.save()`

### Permission Denied
- Verify user has correct permissions
- Check permission classes are properly configured
- Ensure authentication is working

### Database Errors
- Run `python manage.py makemigrations` after model changes
- Run `python manage.py migrate` to apply migrations
- Check foreign key relationships are correct

Remember to test your solutions thoroughly and refer back to the tutorial documentation when needed!