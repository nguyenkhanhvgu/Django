# Monitoring and Logging Implementation

import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
import psutil
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.conf import settings
from django.db import connection
import logging.config

# Structured logging formatter
class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'logger': record.name,
            'level': record.levelname,
            'message': self.getMessage(record),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        
        # Add exception info
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        return json.dumps(log_entry)

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'structured': {
            '()': 'myapp.logging_conf.StructuredFormatter',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'structured',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/app.log',
            'maxBytes': 1024*1024*100,  # 100MB
            'backupCount': 10,
            'formatter': 'structured',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/error.log',
            'maxBytes': 1024*1024*100,  # 100MB
            'backupCount': 10,
            'formatter': 'structured',
            'level': 'ERROR',
        },
        'syslog': {
            'class': 'logging.handlers.SysLogHandler',
            'address': ('localhost', 514),
            'formatter': 'structured',
            'level': 'ERROR',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'myapp': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if settings.DEBUG else 'INFO',
            'propagate': False,
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    }
}

# Request logging middleware
class RequestLoggingMiddleware:
    """Middleware to log all requests with timing and user info"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('myapp.requests')
    
    def __call__(self, request):
        # Generate unique request ID
        request.request_id = str(uuid.uuid4())
        request.start_time = datetime.utcnow()
        
        # Log request start
        self.logger.info(
            'Request started',
            extra={
                'request_id': request.request_id,
                'method': request.method,
                'path': request.path,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
            }
        )
        
        response = self.get_response(request)
        
        # Log request completion
        duration = (datetime.utcnow() - request.start_time).total_seconds()
        
        self.logger.info(
            'Request completed',
            extra={
                'request_id': request.request_id,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': duration,
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
            }
        )
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions with request context"""
        duration = (datetime.utcnow() - request.start_time).total_seconds()
        
        self.logger.error(
            'Request failed with exception',
            extra={
                'request_id': getattr(request, 'request_id', ''),
                'method': request.method,
                'path': request.path,
                'duration': duration,
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
            },
            exc_info=True
        )
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

# Performance monitoring decorator
def monitor_performance(func_name=None):
    """Decorator to monitor function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger('myapp.performance')
            start_time = datetime.utcnow()
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                logger.info(
                    f'Function {func_name or func.__name__} completed',
                    extra={
                        'function': func_name or func.__name__,
                        'duration': duration,
                        'success': True,
                    }
                )
                
                return result
                
            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                logger.error(
                    f'Function {func_name or func.__name__} failed',
                    extra={
                        'function': func_name or func.__name__,
                        'duration': duration,
                        'success': False,
                        'error': str(e),
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator

# Example monitored function
@monitor_performance('user_creation')
def create_user_with_profile(user_data, profile_data):
    """Create user and profile - monitored function"""
    logger = logging.getLogger('myapp.users')
    
    try:
        user = User.objects.create(**user_data)
        profile = UserProfile.objects.create(user=user, **profile_data)
        
        logger.info(
            'User profile created successfully',
            extra={
                'user_id': user.id,
                'username': user.username,
            }
        )
        
        return user
        
    except Exception as e:
        logger.error(
            'Failed to create user profile',
            extra={
                'user_data': user_data,
                'error': str(e),
            },
            exc_info=True
        )
        raise

# System metrics collection
class SystemMetricsCollector:
    """Collect system-level metrics"""
    
    def __init__(self):
        self.process = psutil.Process()
    
    def collect_system_metrics(self) -> dict:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            process_memory = self.process.memory_info()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_metrics = {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv,
                }
            except Exception:
                network_metrics = {}
            
            # Database connection metrics
            db_metrics = self._get_database_metrics()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'process_rss': process_memory.rss,
                    'process_vms': process_memory.vms,
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent,
                },
                'network': network_metrics,
                'database': db_metrics,
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_database_metrics(self) -> dict:
        """Get database connection metrics"""
        try:
            # PostgreSQL specific queries
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity
                    WHERE datname = current_database();
                """)
                result = cursor.fetchone()
                
                return {
                    'total_connections': result[0],
                    'active_connections': result[1],
                    'idle_connections': result[2],
                }
                
        except Exception as e:
            return {'error': str(e)}

# Global metrics collector
metrics = SystemMetricsCollector()

# Application metrics collection
class MetricsCollector:
    """Collect application-level metrics"""
    
    def __init__(self, maxlen=1000):
        self.metrics = defaultdict(lambda: deque(maxlen=maxlen))
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.lock = threading.Lock()
    
    def increment_counter(self, name: str, value: int = 1, tags: dict = None):
        """Increment a counter metric"""
        with self.lock:
            key = self._make_key(name, tags)
            self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, tags: dict = None):
        """Set a gauge metric"""
        with self.lock:
            key = self._make_key(name, tags)
            self.gauges[key] = value
    
    def record_histogram(self, name: str, value: float, tags: dict = None):
        """Record a histogram value"""
        with self.lock:
            key = self._make_key(name, tags)
            self.histograms[key].append(value)
            
            # Keep only recent values
            if len(self.histograms[key]) > 1000:
                self.histograms[key] = self.histograms[key][-1000:]
    
    def record_timing(self, name: str, duration: float, tags: dict = None):
        """Record a timing metric"""
        self.record_histogram(f"{name}.duration", duration, tags)
        self.increment_counter(f"{name}.count", 1, tags)
    
    def _make_key(self, name: str, tags: dict = None) -> str:
        """Create metric key with tags"""
        if not tags:
            return name
        
        tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def get_metrics(self) -> dict:
        """Get all current metrics"""
        with self.lock:
            return {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {
                    k: {
                        'count': len(v),
                        'min': min(v) if v else 0,
                        'max': max(v) if v else 0,
                        'avg': sum(v) / len(v) if v else 0,
                        'p95': self._percentile(v, 0.95) if v else 0,
                        'p99': self._percentile(v, 0.99) if v else 0,
                    }
                    for k, v in self.histograms.items()
                }
            }
    
    def _percentile(self, values: list, percentile: float) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0
        
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]

# Global metrics collector
metrics_collector = MetricsCollector()

# Metrics middleware
class MetricsMiddleware:
    """Middleware to collect request metrics"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        request._metrics_start_time = start_time
        
        response = self.get_response(request)
        
        # Record metrics
        duration = time.time() - start_time
        
        tags = {
            'method': request.method,
            'status_code': response.status_code,
            'path': request.path,
        }
        
        metrics_collector.increment_counter('http.requests.total', tags=tags)
        metrics_collector.record_timing('http.request', duration, tags)
        
        return response

# Health check system
class HealthChecker:
    """System health monitoring"""
    
    def __init__(self):
        self.checks = {}
        self.system_metrics = SystemMetricsCollector()
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check"""
        self.checks[name] = check_func
    
    def run_health_checks(self) -> dict:
        """Run all health checks"""
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'checks': {},
            'system_metrics': self.system_metrics.collect_system_metrics(),
        }
        
        for name, check_func in self.checks.items():
            start_time = time.time()
            
            try:
                check_result = check_func()
                duration = time.time() - start_time
                
                results['checks'][name] = {
                    'status': 'healthy' if check_result else 'unhealthy',
                    'duration': duration,
                    'details': check_result if isinstance(check_result, dict) else {},
                }
                
                if not check_result:
                    results['status'] = 'unhealthy'
                    
            except Exception as e:
                duration = time.time() - start_time
                
                results['checks'][name] = {
                    'status': 'error',
                    'duration': duration,
                    'error': str(e),
                }
                results['status'] = 'unhealthy'
        
        return results

# Initialize health checker
health_checker = HealthChecker()

# Health check functions
def check_database_connection():
    """Check database connectivity"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except Exception:
        return False

def check_cache_connection():
    """Check cache connectivity"""
    try:
        cache.set('health_check', 'ok', 10)
        return cache.get('health_check') == 'ok'
    except Exception:
        return False

def check_disk_space():
    """Check available disk space"""
    try:
        disk = psutil.disk_usage('/')
        free_percent = (disk.free / disk.total) * 100
        return free_percent > 10  # Alert if less than 10% free
    except Exception:
        return False

def check_memory_usage():
    """Check memory usage"""
    try:
        memory = psutil.virtual_memory()
        return memory.percent < 90  # Alert if more than 90% used
    except Exception:
        return False

# Register health checks
health_checker.register_check('database', check_database_connection)
health_checker.register_check('cache', check_cache_connection)
health_checker.register_check('disk_space', check_disk_space)
health_checker.register_check('memory', check_memory_usage)

# Views for metrics and health
@require_http_methods(["GET"])
def health_check_view(request):
    """Health check endpoint"""
    health_status = health_checker.run_health_checks()
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)

@require_http_methods(["GET"])
def metrics_view(request):
    """Metrics endpoint"""
    system_metrics = metrics.collect_system_metrics()
    app_metrics = metrics_collector.get_metrics()
    
    return JsonResponse({
        'system_metrics': system_metrics,
        'application_metrics': app_metrics,
    })

# Usage examples
if __name__ == "__main__":
    # Example usage of monitoring and logging
    
    # Configure logging
    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger('myapp')
    
    # Log some events
    logger.info('Application started')
    logger.warning('This is a warning message', extra={'user_id': 123})
    
    # Collect metrics
    metrics_collector.increment_counter('user.login', tags={'method': 'email'})
    metrics_collector.set_gauge('active_users', 150)
    metrics_collector.record_timing('database.query', 0.025, tags={'table': 'users'})
    
    # Run health checks
    health_status = health_checker.run_health_checks()
    print(f"Health status: {health_status['status']}")
    
    # Get current metrics
    current_metrics = metrics_collector.get_metrics()
    print(f"Current metrics: {current_metrics}")