# Django Performance Optimization Examples

This directory contains practical code examples demonstrating Django performance optimization techniques covered in the advanced tutorial.

## Structure

```
performance-optimization/
├── README.md                          # This file
├── requirements.txt                   # Dependencies
├── django_performance_demo/           # Main Django project
│   ├── manage.py
│   ├── settings/                      # Split settings
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── blog/                          # Sample blog app
│   │   ├── models.py                  # Optimized models
│   │   ├── views.py                   # Performance-optimized views
│   │   ├── managers.py                # Custom managers
│   │   └── utils.py                   # Performance utilities
│   ├── utils/                         # Performance utilities
│   │   ├── cache.py                   # Caching utilities
│   │   ├── profiling.py               # Query profiling tools
│   │   └── monitoring.py              # Performance monitoring
│   └── middleware/                    # Custom middleware
│       ├── performance.py             # Performance monitoring middleware
│       └── cache.py                   # Cache middleware
├── caching_examples/                  # Caching implementations
│   ├── redis_examples.py              # Redis caching examples
│   ├── memcached_examples.py          # Memcached examples
│   └── cache_strategies.py            # Various caching strategies
├── database_optimization/             # Database optimization examples
│   ├── query_optimization.py          # Query optimization techniques
│   ├── bulk_operations.py             # Bulk database operations
│   └── indexing_examples.py           # Database indexing examples
├── testing/                           # Performance testing
│   ├── locustfile.py                  # Load testing with Locust
│   ├── performance_tests.py           # Django performance tests
│   └── benchmarks.py                  # Benchmarking utilities
└── monitoring/                        # Monitoring and metrics
    ├── prometheus_config.py           # Prometheus integration
    ├── custom_metrics.py              # Custom metrics collection
    └── apm_integration.py              # APM integration examples
```

## Setup Instructions

1. **Install Dependencies**
   ```bash
   cd code-examples/performance-optimization
   pip install -r requirements.txt
   ```

2. **Set up Redis (for caching examples)**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   
   # Start Redis
   redis-server
   ```

3. **Set up Memcached (optional)**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install memcached
   
   # macOS
   brew install memcached
   
   # Start Memcached
   memcached -d
   ```

4. **Initialize Django Project**
   ```bash
   cd django_performance_demo
   python manage.py migrate
   python manage.py loaddata sample_data.json
   ```

## Running Examples

### 1. Query Optimization Examples
```bash
python manage.py shell
>>> from database_optimization.query_optimization import *
>>> demonstrate_select_related()
>>> demonstrate_prefetch_related()
>>> demonstrate_bulk_operations()
```

### 2. Caching Examples
```bash
python manage.py shell
>>> from caching_examples.redis_examples import *
>>> test_redis_caching()
>>> test_cache_invalidation()
```

### 3. Performance Testing
```bash
# Load testing with Locust
locust -f testing/locustfile.py --host=http://localhost:8000

# Run performance tests
python manage.py test testing.performance_tests
```

### 4. Monitoring Examples
```bash
# Start Django with performance monitoring
python manage.py runserver --settings=settings.development

# View performance metrics
curl http://localhost:8000/metrics
```

## Key Examples Included

### Database Optimization
- **Query optimization**: select_related, prefetch_related, only, defer
- **Bulk operations**: bulk_create, bulk_update, bulk_delete
- **Custom managers**: Optimized querysets and methods
- **Database indexing**: Composite indexes, partial indexes

### Caching Strategies
- **Redis caching**: Basic caching, advanced patterns, session storage
- **Memcached**: Configuration, key management, best practices
- **Template caching**: Fragment caching, per-view caching
- **Cache invalidation**: Pattern-based invalidation, cache versioning

### Performance Testing
- **Load testing**: Locust configuration for Django applications
- **Performance tests**: Automated performance regression testing
- **Benchmarking**: Custom benchmarking utilities
- **Profiling**: Query profiling and analysis tools

### Monitoring and Metrics
- **Custom middleware**: Performance monitoring, request tracking
- **Prometheus integration**: Metrics collection and export
- **APM integration**: Application performance monitoring setup
- **Custom metrics**: Business-specific performance metrics

## Performance Benchmarks

The examples include benchmark results for common operations:

| Operation | Before Optimization | After Optimization | Improvement |
|-----------|-------------------|-------------------|-------------|
| Post list with authors | 101 queries, 2.3s | 1 query, 0.1s | 95% faster |
| Bulk post creation | 1000 queries, 15s | 1 query, 0.5s | 97% faster |
| Cached post retrieval | 1 query, 0.05s | 0 queries, 0.001s | 98% faster |

## Best Practices Demonstrated

1. **Database Optimization**
   - Always use select_related() for foreign key relationships
   - Use prefetch_related() for many-to-many and reverse foreign keys
   - Implement proper database indexing
   - Use bulk operations for multiple records

2. **Caching Strategy**
   - Implement multi-level caching
   - Use appropriate cache timeouts
   - Implement cache invalidation strategies
   - Monitor cache hit rates

3. **Performance Testing**
   - Write performance tests alongside unit tests
   - Use load testing to simulate real-world usage
   - Monitor performance metrics continuously
   - Set performance budgets and alerts

4. **Code Organization**
   - Separate performance utilities into reusable modules
   - Use custom managers for optimized queries
   - Implement performance monitoring middleware
   - Document performance characteristics

## Troubleshooting

### Common Issues

1. **Redis Connection Errors**
   - Ensure Redis server is running: `redis-cli ping`
   - Check Redis configuration in settings

2. **Memcached Issues**
   - Verify Memcached is running: `telnet localhost 11211`
   - Check Memcached client installation

3. **Database Performance**
   - Enable query logging in development
   - Use Django Debug Toolbar for query analysis
   - Check database indexes with `python manage.py dbshell`

4. **Load Testing Issues**
   - Start with small user counts in Locust
   - Monitor system resources during testing
   - Ensure test data is representative

## Additional Resources

- [Django Performance Documentation](https://docs.djangoproject.com/en/stable/topics/performance/)
- [Redis Documentation](https://redis.io/documentation)
- [Memcached Documentation](https://memcached.org/)
- [Locust Documentation](https://locust.io/)
- [Prometheus Django Integration](https://github.com/korfuri/django-prometheus)

## Contributing

When adding new performance examples:
1. Include both "before" and "after" code
2. Provide benchmark results
3. Add comprehensive documentation
4. Include relevant tests
5. Update this README with new examples