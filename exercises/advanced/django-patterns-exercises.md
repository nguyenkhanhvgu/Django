# Advanced Django Patterns - Exercises

## Exercise 1: Custom Middleware Development

### Objective
Create custom middleware components that demonstrate request/response processing and cross-cutting concerns.

### Tasks

#### 1.1 Security Headers Middleware
Create middleware that adds security headers to all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

**Requirements:**
- Apply headers to all responses except admin pages
- Allow configuration through Django settings
- Log when headers are applied

#### 1.2 Request Timing Middleware
Develop middleware that:
- Measures request processing time
- Logs slow requests (configurable threshold)
- Adds timing information to response headers
- Stores timing data for analytics

#### 1.3 API Versioning Middleware
Build middleware that:
- Extracts API version from headers or URL
- Sets appropriate version context for views
- Handles version deprecation warnings
- Provides fallback for missing version info

### Solution Guidelines
- Use proper middleware structure with `__init__` and `__call__`
- Handle exceptions gracefully
- Consider performance implications
- Test with different request types

---

## Exercise 2: Django Signals Implementation

### Objective
Implement a comprehensive event-driven system using Django signals for blog functionality.

### Tasks

#### 2.1 Content Moderation System
Create a signal-based content moderation system:
- Auto-flag posts with suspicious content
- Send notifications to moderators
- Track moderation actions
- Implement approval workflows

#### 2.2 User Activity Tracking
Build an activity tracking system using signals:
- Track user login/logout events
- Monitor post creation and updates
- Record comment interactions
- Generate activity feeds

#### 2.3 Cache Invalidation System
Implement cache invalidation using signals:
- Clear relevant caches when posts are updated
- Invalidate user-specific caches on profile changes
- Handle tag and category cache updates
- Implement smart cache warming

### Solution Guidelines
- Use both built-in and custom signals
- Implement proper error handling in signal handlers
- Consider signal ordering and dependencies
- Test signal behavior thoroughly

---

## Exercise 3: Advanced ORM Techniques

### Objective
Demonstrate advanced ORM patterns including custom managers, querysets, and database optimization.

### Tasks

#### 3.1 Analytics Manager
Create a custom manager for analytics queries:
- Most popular posts by time period
- User engagement metrics
- Content performance analysis
- Trending topics identification

#### 3.2 Soft Delete Implementation
Implement soft delete functionality:
- Custom manager that excludes deleted records
- Restore functionality for soft-deleted items
- Admin interface for managing deleted content
- Audit trail for deletion actions

#### 3.3 Multi-tenant QuerySet
Build a multi-tenant aware queryset:
- Filter data by tenant automatically
- Handle cross-tenant queries safely
- Implement tenant-specific caching
- Provide tenant switching capabilities

### Solution Guidelines
- Use custom QuerySet and Manager classes
- Optimize database queries with select_related/prefetch_related
- Implement proper indexing strategies
- Consider database-level constraints

---

## Exercise 4: Design Pattern Implementation

### Objective
Apply classic design patterns to solve common Django development challenges.

### Tasks

#### 4.1 Content Processing Strategy
Implement the Strategy pattern for content processing:
- Multiple content formats (Markdown, HTML, Plain text)
- Pluggable processing strategies
- Runtime strategy selection
- Processing pipeline support

#### 4.2 Notification Observer System
Create an Observer pattern for notifications:
- Multiple notification channels (email, SMS, push)
- Event-based notification triggering
- User preference management
- Delivery status tracking

#### 4.3 Command Pattern for Actions
Implement the Command pattern for user actions:
- Undoable operations (post creation, deletion)
- Batch operation support
- Action history and replay
- Permission-based command execution

#### 4.4 Factory Pattern for Content Creation
Build a Factory pattern for content creation:
- Different content types (blog posts, news, tutorials)
- Template-based content generation
- Metadata and configuration management
- Validation and preprocessing

### Solution Guidelines
- Follow SOLID principles
- Implement proper abstractions
- Consider extensibility and maintainability
- Document pattern usage and benefits

---

## Exercise 5: Integration Exercise

### Objective
Combine multiple patterns to build a comprehensive blog management system.

### Tasks

#### 5.1 Complete Blog API
Build a REST API that uses:
- Repository pattern for data access
- Service layer for business logic
- Custom middleware for authentication
- Signal-based event handling

#### 5.2 Content Management Dashboard
Create a dashboard that demonstrates:
- Factory pattern for widget creation
- Observer pattern for real-time updates
- Strategy pattern for data visualization
- Command pattern for bulk operations

#### 5.3 Performance Optimization
Implement performance optimizations using:
- Custom managers for efficient queries
- Caching strategies with signal-based invalidation
- Database optimization techniques
- Middleware for request optimization

### Solution Guidelines
- Integrate patterns seamlessly
- Maintain clean architecture
- Implement comprehensive testing
- Document architectural decisions

---

## Testing Requirements

For all exercises, implement:

### Unit Tests
- Test individual components in isolation
- Mock external dependencies
- Cover edge cases and error conditions
- Achieve high test coverage

### Integration Tests
- Test component interactions
- Verify signal handling
- Test middleware behavior
- Validate database operations

### Performance Tests
- Measure query performance
- Test caching effectiveness
- Validate middleware overhead
- Monitor memory usage

---

## Evaluation Criteria

### Code Quality (25%)
- Clean, readable code
- Proper error handling
- Appropriate documentation
- Following Django conventions

### Pattern Implementation (25%)
- Correct pattern usage
- Proper abstractions
- Extensible design
- SOLID principles adherence

### Functionality (25%)
- Requirements fulfillment
- Edge case handling
- User experience considerations
- Performance optimization

### Testing (25%)
- Comprehensive test coverage
- Proper test structure
- Integration test quality
- Performance validation

---

## Bonus Challenges

### Advanced Middleware
- Implement request/response compression
- Create custom authentication backends
- Build rate limiting with Redis
- Develop request routing middleware

### Complex Signals
- Implement event sourcing with signals
- Create signal-based workflow engine
- Build real-time notification system
- Develop audit logging framework

### ORM Mastery
- Implement database sharding
- Create custom database functions
- Build query optimization tools
- Develop migration utilities

### Pattern Combinations
- Combine multiple patterns effectively
- Create pattern-based frameworks
- Build reusable pattern libraries
- Document pattern interactions

---

## Resources

### Documentation
- Django Official Documentation
- Python Design Patterns Guide
- Database Optimization Best Practices
- Testing Strategies Documentation

### Tools
- Django Debug Toolbar
- Django Extensions
- Coverage.py for test coverage
- Memory profiler for performance testing

### Example Code
- Reference implementations in code-examples/
- Pattern demonstration projects
- Performance benchmarking scripts
- Testing utilities and helpers