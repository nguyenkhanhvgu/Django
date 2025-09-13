"""
Performance monitoring middleware.
"""

import time
import logging
from django.db import connection
from django.conf import settings
from utils.profiling import PerformanceMonitor

logger = logging.getLogger('performance')


class PerformanceMiddleware:
    """Middleware to monitor and log performance metrics."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Start monitoring
        start_time = time.time()
        start_queries = len(connection.queries)
        
        # Process request
        response = self.get_response(request)
        
        # Calculate metrics
        end_time = time.time()
        end_queries = len(connection.queries)
        
        total_time = end_time - start_time
        query_count = end_queries - start_queries
        
        # Log performance metrics
        self._log_performance_metrics(request, response, total_time, query_count)
        
        # Add performance headers
        response['X-Response-Time'] = f"{total_time:.4f}"
        response['X-Query-Count'] = str(query_count)
        
        # Log warnings for slow requests
        self._check_performance_thresholds(request, total_time, query_count)
        
        return response
    
    def _log_performance_metrics(self, request, response, total_time, query_count):
        """Log detailed performance metrics."""
        metrics = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'response_time': f"{total_time:.4f}s",
            'query_count': query_count,
            'user': request.user.username if request.user.is_authenticated else 'Anonymous',
        }
        
        # Add content length if available
        if hasattr(response, 'content'):
            metrics['content_length'] = len(response.content)
        
        logger.info(f"Request metrics: {metrics}")
    
    def _check_performance_thresholds(self, request, total_time, query_count):
        """Check performance thresholds and log warnings."""
        # Configurable thresholds
        slow_request_threshold = getattr(settings, 'SLOW_REQUEST_THRESHOLD', 1.0)
        high_query_threshold = getattr(settings, 'HIGH_QUERY_THRESHOLD', 20)
        
        if total_time > slow_request_threshold:
            logger.warning(
                f"Slow request detected: {request.path} took {total_time:.4f}s "
                f"(threshold: {slow_request_threshold}s)"
            )
        
        if query_count > high_query_threshold:
            logger.warning(
                f"High query count: {request.path} executed {query_count} queries "
                f"(threshold: {high_query_threshold})"
            )
            
            # Log individual queries in debug mode
            if settings.DEBUG:
                recent_queries = connection.queries[-query_count:]
                for i, query in enumerate(recent_queries, 1):
                    logger.debug(f"Query #{i} ({query['time']}s): {query['sql']}")


class QueryCountMiddleware:
    """Middleware specifically for monitoring database query counts."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        end_queries = len(connection.queries)
        query_count = end_queries - start_queries
        
        # Add query count to response headers
        response['X-DB-Query-Count'] = str(query_count)
        
        # Log if query count is high
        if query_count > 10:
            logger.warning(f"High query count for {request.path}: {query_count} queries")
        
        return response


class CacheHitRateMiddleware:
    """Middleware to monitor cache hit rates."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get initial cache stats
        initial_stats = self._get_cache_stats()
        
        response = self.get_response(request)
        
        # Get final cache stats
        final_stats = self._get_cache_stats()
        
        # Calculate hit rate for this request
        if initial_stats and final_stats:
            hits_diff = final_stats.get('hits', 0) - initial_stats.get('hits', 0)
            misses_diff = final_stats.get('misses', 0) - initial_stats.get('misses', 0)
            total_operations = hits_diff + misses_diff
            
            if total_operations > 0:
                hit_rate = (hits_diff / total_operations) * 100
                response['X-Cache-Hit-Rate'] = f"{hit_rate:.1f}%"
                
                if hit_rate < 50:  # Low hit rate threshold
                    logger.warning(f"Low cache hit rate for {request.path}: {hit_rate:.1f}%")
        
        return response
    
    def _get_cache_stats(self):
        """Get cache statistics from Redis."""
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            info = redis_conn.info()
            return {
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0)
            }
        except:
            return None


class MemoryUsageMiddleware:
    """Middleware to monitor memory usage."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        initial_memory = self._get_memory_usage()
        
        response = self.get_response(request)
        
        final_memory = self._get_memory_usage()
        
        if initial_memory and final_memory:
            memory_diff = final_memory - initial_memory
            response['X-Memory-Usage'] = f"{final_memory:.1f}MB"
            response['X-Memory-Diff'] = f"{memory_diff:+.1f}MB"
            
            # Log high memory usage
            if memory_diff > 10:  # 10MB threshold
                logger.warning(f"High memory usage for {request.path}: +{memory_diff:.1f}MB")
        
        return response
    
    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return None


class DetailedPerformanceMiddleware:
    """Comprehensive performance monitoring middleware."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Start comprehensive monitoring
        PerformanceMonitor.start_request_monitoring(request)
        
        # Get initial metrics
        initial_memory = self._get_memory_usage()
        initial_cache_stats = self._get_cache_stats()
        
        # Process request
        response = self.get_response(request)
        
        # Get final metrics
        final_memory = self._get_memory_usage()
        final_cache_stats = self._get_cache_stats()
        
        # Calculate and log comprehensive metrics
        self._log_comprehensive_metrics(
            request, response, initial_memory, final_memory,
            initial_cache_stats, final_cache_stats
        )
        
        return response
    
    def _log_comprehensive_metrics(self, request, response, initial_memory, 
                                 final_memory, initial_cache_stats, final_cache_stats):
        """Log comprehensive performance metrics."""
        execution_time = time.time() - request._performance_start_time
        query_count = len(connection.queries) - request._performance_start_queries
        
        metrics = {
            'path': request.path,
            'method': request.method,
            'status_code': response.status_code,
            'execution_time': f"{execution_time:.4f}s",
            'query_count': query_count,
        }
        
        # Add memory metrics
        if initial_memory and final_memory:
            memory_diff = final_memory - initial_memory
            metrics.update({
                'memory_initial': f"{initial_memory:.1f}MB",
                'memory_final': f"{final_memory:.1f}MB",
                'memory_diff': f"{memory_diff:+.1f}MB"
            })
        
        # Add cache metrics
        if initial_cache_stats and final_cache_stats:
            hits_diff = final_cache_stats.get('hits', 0) - initial_cache_stats.get('hits', 0)
            misses_diff = final_cache_stats.get('misses', 0) - initial_cache_stats.get('misses', 0)
            total_ops = hits_diff + misses_diff
            
            if total_ops > 0:
                hit_rate = (hits_diff / total_ops) * 100
                metrics.update({
                    'cache_hits': hits_diff,
                    'cache_misses': misses_diff,
                    'cache_hit_rate': f"{hit_rate:.1f}%"
                })
        
        logger.info(f"Comprehensive metrics: {metrics}")
    
    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return None
    
    def _get_cache_stats(self):
        """Get cache statistics."""
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            info = redis_conn.info()
            return {
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0)
            }
        except:
            return None