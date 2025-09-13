# Advanced Testing Exercises

These exercises are designed to help you practice comprehensive testing strategies in Django applications. Each exercise builds upon the concepts covered in the comprehensive testing tutorial.

## Exercise 1: Unit Testing Mastery

### Objective
Create comprehensive unit tests for a Django model with complex business logic.

### Scenario
You have a `BlogPost` model with the following features:
- Automatic slug generation from title
- Reading time calculation based on content
- Publication status management
- View count tracking
- SEO score calculation

### Tasks

1. **Model Testing**
   - Write tests for slug generation with edge cases (special characters, duplicates)
   - Test reading time calculation for various content lengths
   - Verify publication status transitions
   - Test view count increment functionality
   - Validate SEO score calculation logic

2. **Validation Testing**
   - Test field validation (title length, content requirements)
   - Test custom model validation methods
   - Verify constraint enforcement (unique slugs, publication dates)

3. **Manager Testing**
   - Test custom managers (published posts, featured posts)
   - Verify queryset methods and filtering
   - Test ordering and pagination

### Expected Deliverables
- Complete test file with at least 15 test methods
- 100% code coverage for the model
- Tests for both happy path and edge cases
- Proper use of setUp and tearDown methods

### Solution Template
```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from blog.models import BlogPost

class BlogPostModelTest(TestCase):
    def setUp(self):
        # Your setup code here
        pass
    
    def test_slug_generation_from_title(self):
        # Test automatic slug generation
        pass
    
    def test_reading_time_calculation(self):
        # Test reading time calculation
        pass
    
    # Add more test methods...
```

## Exercise 2: Integration Testing Challenge

### Objective
Build integration tests for a complete blog workflow involving multiple models and services.

### Scenario
Create tests for a blog publishing workflow that involves:
- User authentication
- Post creation and editing
- Comment moderation
- Email notifications
- Search indexing

### Tasks

1. **Workflow Testing**
   - Test complete post creation workflow (draft → review → publish)
   - Verify comment submission and moderation process
   - Test notification system integration
   - Validate search index updates

2. **Service Integration**
   - Test email service integration with mocking
   - Verify external API calls (social media sharing)
   - Test file upload and processing
   - Validate caching mechanisms

3. **Database Integration**
   - Test transaction handling and rollbacks
   - Verify database constraints and relationships
   - Test bulk operations and performance
   - Validate data consistency across operations

### Expected Deliverables
- Integration test suite with at least 10 test scenarios
- Proper use of mocking for external services
- Transaction testing with rollback scenarios
- Performance benchmarks for critical operations

## Exercise 3: Test-Driven Development (TDD) Project

### Objective
Build a comment system using strict TDD methodology.

### Scenario
Implement a comment system with the following features:
- Nested comments (replies)
- Comment voting (upvote/downvote)
- Spam detection
- Moderation workflow

### Tasks

1. **Red Phase** - Write failing tests first
   - Test comment creation and validation
   - Test nested comment relationships
   - Test voting functionality
   - Test spam detection algorithms

2. **Green Phase** - Write minimal code to pass tests
   - Implement basic comment model
   - Add voting functionality
   - Create spam detection logic
   - Build moderation system

3. **Refactor Phase** - Improve code while keeping tests green
   - Optimize database queries
   - Improve code organization
   - Add performance enhancements
   - Enhance error handling

### Expected Deliverables
- Complete TDD cycle documentation
- Git commits showing red-green-refactor cycles
- Final implementation with 100% test coverage
- Performance benchmarks before and after refactoring

### TDD Workflow Example
```python
# Step 1: Write failing test
def test_comment_can_have_replies(self):
    parent_comment = Comment.objects.create(...)
    reply = Comment.objects.create(parent=parent_comment, ...)
    self.assertEqual(reply.parent, parent_comment)
    self.assertIn(reply, parent_comment.replies.all())

# Step 2: Run test (should fail)
# Step 3: Write minimal code to pass
# Step 4: Refactor and improve
```

## Exercise 4: Functional Testing with Selenium

### Objective
Create comprehensive functional tests for user interactions.

### Scenario
Test complete user journeys on a blog website:
- User registration and login
- Creating and publishing posts
- Commenting on posts
- Searching and filtering content

### Tasks

1. **User Authentication Flow**
   - Test registration process with validation
   - Test login/logout functionality
   - Test password reset workflow
   - Verify session management

2. **Content Management**
   - Test post creation with rich text editor
   - Test image upload and handling
   - Test draft saving and publishing
   - Verify content preview functionality

3. **Interactive Features**
   - Test comment submission and display
   - Test search functionality with filters
   - Test pagination and infinite scroll
   - Verify responsive design elements

### Expected Deliverables
- Selenium test suite with page object pattern
- Cross-browser testing setup
- Screenshot capture on test failures
- Performance timing measurements

### Page Object Example
```python
class BlogPostPage:
    def __init__(self, driver):
        self.driver = driver
    
    def create_post(self, title, content):
        # Implementation for creating a post
        pass
    
    def submit_comment(self, comment_text):
        # Implementation for submitting a comment
        pass
```

## Exercise 5: Performance Testing Implementation

### Objective
Implement performance testing for a Django blog application.

### Scenario
Create performance tests to ensure the blog can handle:
- 1000 concurrent users
- Database queries under load
- Cache effectiveness
- Memory usage optimization

### Tasks

1. **Load Testing**
   - Create Locust test scenarios
   - Test API endpoints under load
   - Measure response times and throughput
   - Identify performance bottlenecks

2. **Database Performance**
   - Test query performance with large datasets
   - Measure database connection pooling
   - Test transaction handling under load
   - Optimize slow queries

3. **Caching Strategy**
   - Test cache hit/miss ratios
   - Measure cache invalidation performance
   - Test different caching backends
   - Validate cache consistency

### Expected Deliverables
- Locust test files for load testing
- Performance benchmarks and reports
- Database query optimization recommendations
- Caching strategy documentation

### Locust Example
```python
from locust import HttpUser, task, between

class BlogUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_posts(self):
        self.client.get("/blog/")
    
    @task(1)
    def view_post_detail(self):
        self.client.get("/blog/post/1/")
```

## Exercise 6: CI/CD Pipeline Testing

### Objective
Set up a complete CI/CD pipeline with comprehensive testing.

### Scenario
Create a GitHub Actions workflow that:
- Runs tests on multiple Python/Django versions
- Performs code quality checks
- Runs security scans
- Deploys to staging/production

### Tasks

1. **Multi-Environment Testing**
   - Test on Python 3.8, 3.9, 3.10, 3.11
   - Test on Django 3.2, 4.0, 4.1, 4.2
   - Test with different databases (SQLite, PostgreSQL)
   - Test with different cache backends

2. **Quality Assurance**
   - Integrate code formatting (Black, isort)
   - Add linting (flake8, pylint)
   - Include type checking (mypy)
   - Add security scanning (bandit, safety)

3. **Deployment Pipeline**
   - Automated testing before deployment
   - Staging environment deployment
   - Production deployment with approval
   - Rollback mechanisms

### Expected Deliverables
- Complete GitHub Actions workflow file
- Docker configuration for testing
- Environment-specific settings
- Deployment scripts and documentation

## Exercise 7: Advanced Mocking and Patching

### Objective
Master advanced mocking techniques for testing external dependencies.

### Scenario
Test a blog application that integrates with:
- External email service (SendGrid)
- Social media APIs (Twitter, Facebook)
- Image processing service (Cloudinary)
- Analytics service (Google Analytics)

### Tasks

1. **Service Mocking**
   - Mock email service responses
   - Mock social media API calls
   - Mock image processing operations
   - Mock analytics tracking

2. **Error Handling**
   - Test service unavailability scenarios
   - Test rate limiting responses
   - Test authentication failures
   - Test network timeout handling

3. **Integration Testing**
   - Test service failover mechanisms
   - Test retry logic and backoff strategies
   - Test circuit breaker patterns
   - Test graceful degradation

### Expected Deliverables
- Comprehensive mocking test suite
- Error scenario test coverage
- Integration test documentation
- Service reliability testing

### Mocking Example
```python
@patch('blog.services.EmailService.send_email')
def test_post_notification_email_failure(self, mock_send_email):
    mock_send_email.side_effect = EmailServiceException("Service unavailable")
    
    # Test that the application handles email service failure gracefully
    result = PostService.publish_post_with_notification(self.post)
    
    self.assertTrue(result.published)
    self.assertFalse(result.notification_sent)
    self.assertIn("Email service unavailable", result.errors)
```

## Exercise 8: Custom Test Assertions and Utilities

### Objective
Create custom test assertions and utilities for domain-specific testing.

### Scenario
Build a testing framework extension for blog-specific assertions:
- Content quality assertions
- SEO compliance checks
- Accessibility testing
- Performance assertions

### Tasks

1. **Custom Assertions**
   - Create assertions for content validation
   - Build SEO compliance checkers
   - Add accessibility test helpers
   - Implement performance benchmarks

2. **Test Utilities**
   - Create test data builders
   - Build database state helpers
   - Add email testing utilities
   - Create API response validators

3. **Test Decorators**
   - Create performance timing decorators
   - Build database state decorators
   - Add feature flag decorators
   - Implement retry decorators

### Expected Deliverables
- Custom assertion library
- Test utility functions
- Decorator implementations
- Documentation and usage examples

### Custom Assertion Example
```python
class BlogTestCase(TestCase):
    def assertValidSEO(self, post):
        """Assert that a post meets SEO requirements"""
        self.assertIsNotNone(post.meta_description)
        self.assertLessEqual(len(post.title), 60)
        self.assertGreaterEqual(len(post.content), 300)
        self.assertTrue(post.has_featured_image())
    
    def assertEmailSent(self, subject_contains=None, to_email=None):
        """Assert that an email was sent with specific criteria"""
        # Implementation here
        pass
```

## Bonus Challenge: Complete Testing Strategy

### Objective
Design and implement a complete testing strategy for a production Django blog application.

### Requirements
- Unit tests with 95%+ coverage
- Integration tests for all workflows
- Functional tests for user journeys
- Performance tests with benchmarks
- Security testing implementation
- CI/CD pipeline with multiple environments
- Monitoring and alerting for test failures

### Deliverables
- Complete test suite (500+ tests)
- CI/CD pipeline configuration
- Performance benchmarking reports
- Security testing documentation
- Test strategy documentation
- Maintenance and scaling guidelines

## Evaluation Criteria

For each exercise, you will be evaluated on:

1. **Test Coverage** - Comprehensive coverage of functionality
2. **Test Quality** - Well-written, maintainable tests
3. **Best Practices** - Following Django and Python testing conventions
4. **Documentation** - Clear documentation and comments
5. **Performance** - Efficient test execution
6. **Real-world Applicability** - Practical, production-ready solutions

## Getting Started

1. Choose an exercise that matches your current skill level
2. Set up the development environment
3. Read the scenario and requirements carefully
4. Plan your testing approach
5. Implement tests following TDD principles
6. Document your solution and learnings
7. Share your implementation for feedback

## Resources

- Django Testing Documentation
- pytest-django Documentation
- Factory Boy Documentation
- Selenium WebDriver Documentation
- GitHub Actions Documentation
- Performance Testing Best Practices

Remember: The goal is not just to write tests, but to understand how comprehensive testing improves code quality, reduces bugs, and enables confident refactoring and deployment.