# Django Scalability Examples

This directory contains comprehensive examples for scaling Django applications, including load balancing, database sharding, microservices architecture, and monitoring implementations.

## Contents

### 1. Load Balancing (`load_balancing.py`)
- **Nginx Configuration**: Production-ready load balancer setup with health checks
- **HAProxy Configuration**: Alternative load balancer with round-robin distribution
- **Application-Level Load Balancing**: Python implementations of various load balancing algorithms
- **Session Affinity**: Sticky session implementation for stateful applications
- **Circuit Breaker Pattern**: Resilient load balancing with failure handling
- **Health-Aware Routing**: Intelligent routing based on server health status

**Key Features:**
- Round-robin, weighted random, and least connections algorithms
- Health check integration
- Response time tracking for adaptive load balancing
- Circuit breaker protection against cascading failures

### 2. Database Sharding (`database_sharding.py`)
- **Shard Router**: Django database router for horizontal sharding
- **Consistent Hashing**: Hash-based sharding for better distribution
- **Sharded Models**: Base classes for shard-aware Django models
- **Cross-Shard Queries**: Utilities for querying across multiple shards
- **Shard Management**: Tools for rebalancing and migrating data

**Key Features:**
- Modulo-based and hash-based sharding strategies
- Automatic shard routing for reads and writes
- Cross-shard aggregation and statistics
- Data migration utilities

### 3. Microservices Architecture (`microservices_architecture.py`)
- **Service Registry**: Central service discovery mechanism
- **Service Communication**: Sync and async inter-service communication
- **Event-Driven Architecture**: Event bus for decoupled communication
- **API Gateway**: Request routing and middleware support
- **Circuit Breaker**: Resilient service communication
- **Health Monitoring**: Service health checks and dependency tracking

**Key Features:**
- Service registration and discovery
- RESTful and event-driven communication patterns
- Circuit breaker protection
- Comprehensive error handling

### 4. Monitoring and Logging (`monitoring_logging.py`)
- **Structured Logging**: JSON-formatted logs with context
- **Request Tracking**: Middleware for request logging and timing
- **Performance Monitoring**: Function-level performance tracking
- **System Metrics**: CPU, memory, disk, and network monitoring
- **Application Metrics**: Custom counters, gauges, and histograms
- **Health Checks**: Comprehensive system health monitoring

**Key Features:**
- Structured JSON logging with request correlation
- Real-time system and application metrics
- Health check endpoints
- Performance monitoring decorators

### 5. Docker Configuration (`docker-compose.yml`, `nginx.conf`)
- **Multi-Container Setup**: Complete scalable application stack
- **Load Balancer**: Nginx configuration with SSL and caching
- **Database Replication**: Primary-replica PostgreSQL setup
- **Monitoring Stack**: Prometheus, Grafana, and ELK stack
- **Background Tasks**: Celery workers and scheduler

**Key Features:**
- Production-ready Docker configuration
- SSL termination and security headers
- Rate limiting and caching
- Comprehensive monitoring setup

## Quick Start

### 1. Basic Load Balancing Setup

```python
from load_balancing import ApplicationLoadBalancer

# Initialize load balancer
load_balancer = ApplicationLoadBalancer([
    'http://django-1:8000',
    'http://django-2:8000',
    'http://django-3:8000'
])

# Get server using different strategies
server = load_balancer.round_robin()
server = load_balancer.least_connections()
server = load_balancer.health_aware_routing()
```

### 2. Database Sharding Setup

```python
# settings.py
DATABASE_ROUTERS = ['myapp.routers.HashShardRouter']

DATABASES = {
    'default': {...},
    'shard1': {...},
    'shard2': {...},
    'shard3': {...},
}

# models.py
from database_sharding import ShardedModel

class User(ShardedModel):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    
    def get_shard_key(self):
        return f"user:{self.id}"
```

### 3. Microservices Communication

```python
from microservices_architecture import ServiceRegistry, ServiceClient

# Register services
service_registry.register_service('user-service', 'localhost', 8001)
service_registry.register_service('order-service', 'localhost', 8002)

# Communicate between services
user_client = ServiceClient('user-service')
user_data = user_client.get('/users/123/')
```

### 4. Monitoring Setup

```python
from monitoring_logging import monitor_performance, metrics_collector

@monitor_performance('user_creation')
def create_user(user_data):
    # Function implementation
    pass

# Record custom metrics
metrics_collector.increment_counter('user.login')
metrics_collector.set_gauge('active_users', 150)
metrics_collector.record_timing('database.query', 0.025)
```

### 5. Docker Deployment

```bash
# Start the complete stack
docker-compose up -d

# Scale Django application instances
docker-compose up -d --scale django-app-1=3

# View logs
docker-compose logs -f django-app-1

# Monitor services
docker-compose ps
```

## Configuration Examples

### Django Settings for Scalability

```python
# settings/production.py
import os

# Database configuration with connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        }
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}

# Session configuration for multiple servers
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Static files for CDN
STATIC_URL = os.environ.get('CDN_URL', '/static/')
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

### Nginx Load Balancer Configuration

```nginx
upstream django_app {
    least_conn;
    server django-app-1:8000 weight=3 max_fails=3 fail_timeout=30s;
    server django-app-2:8000 weight=3 max_fails=3 fail_timeout=30s;
    server django-app-3:8000 weight=2 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name example.com;
    
    location / {
        proxy_pass http://django_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Performance Considerations

### 1. Database Optimization
- Use connection pooling to reduce connection overhead
- Implement read replicas for read-heavy workloads
- Consider database sharding for horizontal scaling
- Use database query optimization and indexing

### 2. Caching Strategy
- Implement Redis for session storage and caching
- Use CDN for static file delivery
- Cache database queries and API responses
- Implement cache invalidation strategies

### 3. Application Scaling
- Use horizontal scaling with load balancers
- Implement stateless application design
- Use background task queues for heavy operations
- Monitor application performance and bottlenecks

### 4. Security Considerations
- Implement rate limiting to prevent abuse
- Use SSL/TLS for all communications
- Secure inter-service communication
- Implement proper authentication and authorization

## Monitoring and Alerting

### Key Metrics to Monitor
- **Response Time**: Average and percentile response times
- **Throughput**: Requests per second
- **Error Rate**: 4xx and 5xx error percentages
- **Resource Usage**: CPU, memory, disk, and network utilization
- **Database Performance**: Query times and connection counts
- **Cache Hit Rate**: Cache effectiveness metrics

### Health Check Endpoints
- `/health/` - Basic application health
- `/health/detailed/` - Detailed health with dependencies
- `/metrics/` - Application and system metrics
- `/status/` - Service status and version information

## Troubleshooting

### Common Issues
1. **High Response Times**: Check database queries, add caching, optimize code
2. **Memory Leaks**: Monitor memory usage, check for unclosed connections
3. **Database Connection Errors**: Verify connection pool settings, check database health
4. **Load Balancer Issues**: Check upstream server health, verify configuration
5. **Cache Misses**: Review cache strategy, check cache expiration settings

### Debugging Tools
- Use structured logging for better debugging
- Implement distributed tracing for microservices
- Monitor system metrics continuously
- Use profiling tools for performance analysis

## Best Practices

1. **Design for Failure**: Implement circuit breakers and graceful degradation
2. **Monitor Everything**: Comprehensive monitoring and alerting
3. **Automate Deployments**: Use CI/CD for consistent deployments
4. **Test at Scale**: Load testing and performance testing
5. **Security First**: Implement security best practices from the start
6. **Documentation**: Keep architecture and deployment documentation updated

## Further Reading

- [Django Performance Optimization](../performance-optimization/)
- [Database Scaling Strategies](../database-relationships-demo/)
- [Deployment Best Practices](../deployment-examples/)
- [Monitoring and Observability](../comprehensive-testing/)

## Requirements

```txt
Django>=4.2.0
psycopg2-binary>=2.9.0
redis>=4.5.0
django-redis>=5.2.0
celery>=5.2.0
psutil>=5.9.0
requests>=2.28.0
aiohttp>=3.8.0
```

This scalability guide provides a comprehensive foundation for building and deploying Django applications that can handle high traffic and scale horizontally. Each component can be adapted and extended based on specific requirements and infrastructure constraints.