"""
Custom Performance Metrics Collection for Django

This module demonstrates how to collect and monitor custom performance
metrics in Django applications using various monitoring tools and techniques.
"""

import time
import logging
from functools import wraps
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from prometheus_client import Counter, Histogram, Gauge, Summary
import threading
import psutil
import gc


# Configure logging
logger = logging.getLogger(__name__)


# Prometheus Metrics
REQUEST_COUNT = Counter(
    'django_requests_total',
    'Total Django requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'django_request_duration_seconds',
    'Django request duration',
    ['method', 'endpoint']
)

DATABASE_QUERY_COUNT = Counter(
    'django_database_queries_total',
    'Total database queries',
    ['query_type']
)

DATABASE_QUERY_DURATION = Histogram(
    'django_database_query_duration_seconds',
    'Database query duration'
)

CACHE_OPERATIONS = Counter(
    'django_cache_operations_total',
    'Cache operations',
    ['operation', 'result']
)

ACTIVE_USERS = Gauge(
    'django_active_users',
    'Number of active users'
)

MEMORY_USAGE = Gauge(
    'django_memory_usage_bytes',
    'Memory usage in bytes'
)

RESPONSE_SIZE = Histogram(
    'django_response_size_bytes',
    'Response size in bytes'
)


class PerformanceMetrics:
    """Centralized performance metrics collection"""
    
    def __init__(self):
        self.metrics = {}
        self.lock = threading.Lock()
    
    def record_request(self, method, endpoint, status_code, duration, response_size=0):
        """Record request metrics"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        if response_size > 0:
            RESPONSE_SIZE.observe(response_size)
    
    def record_database_query(self, query_type, duration):
        """Record database query metrics"""
        DATABASE_QUERY_COUNT.labels(query_type=query_type).inc()
        DATABASE_QUERY_DURATION.observe(duration)
    
    def record_cache_operation(self, operation, result):
        """Record cache operation metrics"""
        CACHE_OPERATIONS.labels(operation=operation, result=result).inc()
    
    def update_system_metrics(self):
        """Update system-level metrics"""
        # Memory usage
        process = psutil.Process()
        memory_info = process.memory_info()
        MEMORY_USAGE.set(memory_info.rss)
        
        # Active users (simplified - would use session data in real app)
        active_users = self.get_active_users_count()
        ACTIVE_USERS.set(active_users)
    
    def get_active_users_count(self):
        """Get count of active users (simplified implementation)"""
        # In a real application, this would query session data
        # or use a more sophisticated method
        return cache.get('active_users_count', 0)
    
    def get_custom_metrics(self):
        """Get custom application metrics"""
        with self.lock:
            return self.metrics.copy()
    
    def set_custom_metric(self, name, value):
        """Set a custom metric value"""
        with self.lock:
            self.metrics[name] = {
                'value': value,
                'timestamp': time.time()
            }


# Global metrics instance
performance_metrics = PerformanceMetrics()


class PerformanceMonitoringMiddleware:
    """Middleware for comprehensive performance monitoring"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        start_queries = len(connection.queries)
        
        # Process request
        response = self.get_response(request)
        
        # Calculate metrics
        end_time = time.time()
        duration = end_time - start_time
        end_queries = len(connection.queries)
        query_count = end_queries - start_queries
        
        # Record metrics
        performance_metrics.record_request(
            method=request.method,
            endpoint=self.get_endpoint_name(request),
            status_code=response.status_code,
            duration=duration,
            response_size=len(response.content) if hasattr(response, 'content') else 0
        )
        
        # Log slow requests
        if duration > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.path} - "
                f"Duration: {duration:.2f}s, Queries: {query_count}"
            )
        
        # Log queries if too many
        if query_count > 20:
            logger.warning(
                f"High query count: {request.method} {request.path} - "
                f"Queries: {query_count}, Duration: {duration:.2f}s"
            )
        
        # Add performance headers
        response['X-Response-Time'] = f"{duration:.3f}"
        response['X-Query-Count'] = str(query_count)
        
        return response
    
    def get_endpoint_name(self, request):
        """Get a normalized endpoint name for metrics"""
        path = request.path
        
        # Normalize paths with IDs (e.g., /posts/123/ -> /posts/{id}/)
        import re
        path = re.sub(r'/\d+/', '/{id}/', path)
        
        return path


def performance_monitor(metric_name=None):
    """Decorator for monitoring function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_queries = len(connection.queries)
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                end_queries = len(connection.queries)
                query_count = end_queries - start_queries
                
                # Record custom metric
                name = metric_name or f"{func.__module__}.{func.__name__}"
                performance_metrics.set_custom_metric(f"{name}_duration", duration)
                performance_metrics.set_custom_metric(f"{name}_queries", query_count)
                performance_metrics.set_custom_metric(f"{name}_success", success)
                
                # Log if slow
                if duration > 0.5:
                    logger.info(
                        f"Function {name} took {duration:.3f}s with {query_count} queries"
                    )
            
            return result
        return wrapper
    return decorator


class DatabaseQueryMonitor:
    """Monitor database query performance"""
    
    def __init__(self):
        self.slow_queries = []
        self.query_stats = {}
    
    def analyze_queries(self):
        """Analyze recent database queries"""
        if not settings.DEBUG:
            return
        
        for query in connection.queries:
            query_time = float(query['time'])
            sql = query['sql']
            
            # Categorize query type
            query_type = self.categorize_query(sql)
            
            # Record metrics
            performance_metrics.record_database_query(query_type, query_time)
            
            # Track slow queries
            if query_time > 0.1:  # Queries slower than 100ms
                self.slow_queries.append({
                    'sql': sql[:200] + '...' if len(sql) > 200 else sql,
                    'time': query_time,
                    'timestamp': time.time()
                })
            
            # Update query statistics
            if query_type not in self.query_stats:
                self.query_stats[query_type] = {'count': 0, 'total_time': 0}
            
            self.query_stats[query_type]['count'] += 1
            self.query_stats[query_type]['total_time'] += query_time
    
    def categorize_query(self, sql):
        """Categorize SQL query by type"""
        sql_upper = sql.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'OTHER'
    
    def get_slow_queries(self, limit=10):
        """Get recent slow queries"""
        return sorted(
            self.slow_queries[-100:],  # Last 100 queries
            key=lambda x: x['time'],
            reverse=True
        )[:limit]
    
    def get_query_statistics(self):
        """Get query statistics summary"""
        return self.query_stats


class CacheMonitor:
    """Monitor cache performance"""
    
    def __init__(self):
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def record_hit(self):
        """Record cache hit"""
        self.cache_stats['hits'] += 1
        performance_metrics.record_cache_operation('get', 'hit')
    
    def record_miss(self):
        """Record cache miss"""
        self.cache_stats['misses'] += 1
        performance_metrics.record_cache_operation('get', 'miss')
    
    def record_set(self):
        """Record cache set"""
        self.cache_stats['sets'] += 1
        performance_metrics.record_cache_operation('set', 'success')
    
    def record_delete(self):
        """Record cache delete"""
        self.cache_stats['deletes'] += 1
        performance_metrics.record_cache_operation('delete', 'success')
    
    def get_hit_rate(self):
        """Calculate cache hit rate"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        return (self.cache_stats['hits'] / total * 100) if total > 0 else 0
    
    def get_stats(self):
        """Get cache statistics"""
        stats = self.cache_stats.copy()
        stats['hit_rate'] = self.get_hit_rate()
        return stats


class MemoryMonitor:
    """Monitor memory usage and garbage collection"""
    
    def __init__(self):
        self.gc_stats = []
    
    def collect_memory_stats(self):
        """Collect current memory statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Garbage collection stats
        gc_stats = {
            'generation_0': gc.get_count()[0],
            'generation_1': gc.get_count()[1],
            'generation_2': gc.get_count()[2],
            'total_collections': sum(gc.get_stats()[i]['collections'] for i in range(3))
        }
        
        return {
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': process.memory_percent(),
            'gc_stats': gc_stats,
            'timestamp': time.time()
        }
    
    def force_gc_and_measure(self):
        """Force garbage collection and measure impact"""
        before_stats = self.collect_memory_stats()
        
        # Force garbage collection
        collected = gc.collect()
        
        after_stats = self.collect_memory_stats()
        
        memory_freed = before_stats['rss'] - after_stats['rss']
        
        return {
            'objects_collected': collected,
            'memory_freed': memory_freed,
            'before': before_stats,
            'after': after_stats
        }


class PerformanceReporter:
    """Generate performance reports"""
    
    def __init__(self):
        self.db_monitor = DatabaseQueryMonitor()
        self.cache_monitor = CacheMonitor()
        self.memory_monitor = MemoryMonitor()
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        # Update system metrics
        performance_metrics.update_system_metrics()
        
        # Analyze queries
        self.db_monitor.analyze_queries()
        
        report = {
            'timestamp': time.time(),
            'custom_metrics': performance_metrics.get_custom_metrics(),
            'database': {
                'slow_queries': self.db_monitor.get_slow_queries(),
                'query_stats': self.db_monitor.get_query_statistics()
            },
            'cache': self.cache_monitor.get_stats(),
            'memory': self.memory_monitor.collect_memory_stats(),
            'system': self.get_system_stats()
        }
        
        return report
    
    def get_system_stats(self):
        """Get system-level statistics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    
    def log_performance_summary(self):
        """Log performance summary"""
        report = self.generate_report()
        
        logger.info("=== Performance Summary ===")
        logger.info(f"Memory usage: {report['memory']['percent']:.1f}%")
        logger.info(f"Cache hit rate: {report['cache']['hit_rate']:.1f}%")
        logger.info(f"Slow queries: {len(report['database']['slow_queries'])}")
        logger.info(f"CPU usage: {report['system']['cpu_percent']:.1f}%")


# Global instances
db_monitor = DatabaseQueryMonitor()
cache_monitor = CacheMonitor()
memory_monitor = MemoryMonitor()
performance_reporter = PerformanceReporter()


# Usage examples
@performance_monitor('user_dashboard')
def get_user_dashboard_data(user_id):
    """Example function with performance monitoring"""
    # Simulate database operations
    time.sleep(0.1)
    return {'user_id': user_id, 'data': 'dashboard_data'}


def example_cache_monitoring():
    """Example of cache monitoring"""
    # Simulate cache operations
    cache_key = 'test_key'
    
    # Cache miss
    data = cache.get(cache_key)
    if data is None:
        cache_monitor.record_miss()
        data = 'computed_data'
        cache.set(cache_key, data)
        cache_monitor.record_set()
    else:
        cache_monitor.record_hit()
    
    return data


if __name__ == "__main__":
    # Example usage
    print("Performance Metrics Collection Examples")
    print("=" * 50)
    
    # Generate and display report
    report = performance_reporter.generate_report()
    print(f"Generated performance report at {report['timestamp']}")
    
    # Log performance summary
    performance_reporter.log_performance_summary()