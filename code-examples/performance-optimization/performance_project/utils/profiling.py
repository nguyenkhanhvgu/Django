"""
Profiling utilities for performance optimization.
"""

import time
import functools
import logging
from django.db import connection
from django.conf import settings
from django.core.management.color import no_style
import cProfile
import pstats
import io

logger = logging.getLogger('performance')


class QueryProfiler:
    """Context manager for profiling database queries."""
    
    def __init__(self, log_queries=True, log_slow_queries=True, slow_threshold=0.1):
        """
        Initialize query profiler.
        
        Args:
            log_queries (bool): Whether to log all queries
            log_slow_queries (bool): Whether to log slow queries
            slow_threshold (float): Threshold in seconds for slow queries
        """
        self.log_queries = log_queries
        self.log_slow_queries = log_slow_queries
        self.slow_threshold = slow_threshold
        self.start_queries = 0
        self.start_time = 0
    
    def __enter__(self):
        self.start_queries = len(connection.queries)
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        end_queries = len(connection.queries)
        
        query_count = end_queries - self.start_queries
        execution_time = end_time - self.start_time
        
        # Log summary
        logger.info(f"Queries executed: {query_count}")
        logger.info(f"Total execution time: {execution_time:.4f} seconds")
        
        if query_count > 0:
            avg_query_time = execution_time / query_count
            logger.info(f"Average query time: {avg_query_time:.4f} seconds")
        
        # Log individual queries if enabled
        if self.log_queries and settings.DEBUG:
            queries = connection.queries[self.start_queries:end_queries]
            for i, query in enumerate(queries, 1):
                query_time = float(query['time'])
                sql = query['sql']
                
                if self.log_slow_queries and query_time > self.slow_threshold:
                    logger.warning(f"SLOW QUERY #{i} ({query_time:.4f}s): {sql}")
                else:
                    logger.debug(f"Query #{i} ({query_time:.4f}s): {sql}")
        
        # Warn about potential performance issues
        if query_count > 20:
            logger.warning(f"High query count detected: {query_count} queries")
        
        if execution_time > 1.0:
            logger.warning(f"Slow execution detected: {execution_time:.4f} seconds")


def profile_queries(func):
    """Decorator to profile database queries for a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with QueryProfiler():
            return func(*args, **kwargs)
    return wrapper


class PerformanceProfiler:
    """Context manager for comprehensive performance profiling."""
    
    def __init__(self, profile_code=True, profile_queries=True):
        """
        Initialize performance profiler.
        
        Args:
            profile_code (bool): Whether to profile Python code execution
            profile_queries (bool): Whether to profile database queries
        """
        self.profile_code = profile_code
        self.profile_queries = profile_queries
        self.profiler = None
        self.query_profiler = None
    
    def __enter__(self):
        if self.profile_code:
            self.profiler = cProfile.Profile()
            self.profiler.enable()
        
        if self.profile_queries:
            self.query_profiler = QueryProfiler()
            self.query_profiler.__enter__()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.profile_code and self.profiler:
            self.profiler.disable()
            
            # Generate profiling report
            s = io.StringIO()
            ps = pstats.Stats(self.profiler, stream=s)
            ps.sort_stats('cumulative')
            ps.print_stats(20)  # Top 20 functions
            
            logger.info("Code profiling results:")
            logger.info(s.getvalue())
        
        if self.profile_queries and self.query_profiler:
            self.query_profiler.__exit__(exc_type, exc_val, exc_tb)


def performance_profile(profile_code=True, profile_queries=True):
    """Decorator for comprehensive performance profiling."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceProfiler(profile_code, profile_queries):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class MemoryProfiler:
    """Memory usage profiling utilities."""
    
    @staticmethod
    def get_memory_usage():
        """Get current memory usage in MB."""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return {
                'rss': memory_info.rss / 1024 / 1024,  # MB
                'vms': memory_info.vms / 1024 / 1024,  # MB
                'percent': process.memory_percent()
            }
        except ImportError:
            logger.warning("psutil not available, cannot get memory usage")
            return None
    
    @staticmethod
    def memory_profile(func):
        """Decorator to profile memory usage of a function."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            initial_memory = MemoryProfiler.get_memory_usage()
            
            result = func(*args, **kwargs)
            
            final_memory = MemoryProfiler.get_memory_usage()
            
            if initial_memory and final_memory:
                memory_diff = final_memory['rss'] - initial_memory['rss']
                logger.info(f"Function {func.__name__} memory usage:")
                logger.info(f"  Initial: {initial_memory['rss']:.2f} MB")
                logger.info(f"  Final: {final_memory['rss']:.2f} MB")
                logger.info(f"  Difference: {memory_diff:.2f} MB")
            
            return result
        return wrapper


class TimingProfiler:
    """Simple timing profiler for functions and code blocks."""
    
    def __init__(self, name="Operation"):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        execution_time = end_time - self.start_time
        logger.info(f"{self.name} completed in {execution_time:.4f} seconds")


def timing_profile(name=None):
    """Decorator for timing function execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            operation_name = name or f"Function {func.__name__}"
            with TimingProfiler(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class DatabaseProfiler:
    """Advanced database profiling utilities."""
    
    @staticmethod
    def analyze_queries(queries):
        """
        Analyze a list of queries for performance issues.
        
        Args:
            queries (list): List of query dictionaries from Django
            
        Returns:
            dict: Analysis results
        """
        if not queries:
            return {'total_queries': 0, 'issues': []}
        
        total_time = sum(float(q['time']) for q in queries)
        slow_queries = [q for q in queries if float(q['time']) > 0.1]
        duplicate_queries = DatabaseProfiler._find_duplicate_queries(queries)
        
        issues = []
        
        if len(queries) > 20:
            issues.append(f"High query count: {len(queries)} queries")
        
        if slow_queries:
            issues.append(f"Slow queries detected: {len(slow_queries)} queries > 0.1s")
        
        if duplicate_queries:
            issues.append(f"Duplicate queries detected: {len(duplicate_queries)} duplicates")
        
        return {
            'total_queries': len(queries),
            'total_time': total_time,
            'average_time': total_time / len(queries),
            'slow_queries': len(slow_queries),
            'duplicate_queries': len(duplicate_queries),
            'issues': issues
        }
    
    @staticmethod
    def _find_duplicate_queries(queries):
        """Find duplicate queries in a list."""
        seen_queries = {}
        duplicates = []
        
        for query in queries:
            sql = query['sql']
            if sql in seen_queries:
                duplicates.append(query)
            else:
                seen_queries[sql] = query
        
        return duplicates
    
    @staticmethod
    def explain_query(query_sql):
        """
        Get EXPLAIN output for a query (PostgreSQL).
        
        Args:
            query_sql (str): SQL query to explain
            
        Returns:
            list: EXPLAIN output
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXPLAIN ANALYZE {query_sql}")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error explaining query: {e}")
            return []


class PerformanceMonitor:
    """Performance monitoring utilities."""
    
    @staticmethod
    def log_performance_metrics(request, response, view_name=None):
        """
        Log performance metrics for a request/response cycle.
        
        Args:
            request: Django request object
            response: Django response object
            view_name (str): Name of the view
        """
        if hasattr(request, '_performance_start_time'):
            response_time = time.time() - request._performance_start_time
            
            metrics = {
                'view': view_name or 'Unknown',
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'response_time': response_time,
                'content_length': len(response.content) if hasattr(response, 'content') else 0
            }
            
            # Add query metrics if available
            if hasattr(request, '_performance_start_queries'):
                query_count = len(connection.queries) - request._performance_start_queries
                metrics['query_count'] = query_count
            
            logger.info(f"Performance metrics: {metrics}")
    
    @staticmethod
    def start_request_monitoring(request):
        """Start monitoring a request."""
        request._performance_start_time = time.time()
        request._performance_start_queries = len(connection.queries)
    
    @staticmethod
    def create_performance_report(queries, execution_time):
        """
        Create a comprehensive performance report.
        
        Args:
            queries (list): List of executed queries
            execution_time (float): Total execution time
            
        Returns:
            dict: Performance report
        """
        query_analysis = DatabaseProfiler.analyze_queries(queries)
        memory_usage = MemoryProfiler.get_memory_usage()
        
        return {
            'execution_time': execution_time,
            'database': query_analysis,
            'memory': memory_usage,
            'timestamp': time.time()
        }