"""
Request logging middleware example.
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('middleware')

class RequestLoggingMiddleware:
    """
    Middleware to log request and response details.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Log request details
        logger.info(
            f"Request started: {request.method} {request.path} "
            f"from {self.get_client_ip(request)}"
        )
        
        response = self.get_response(request)
        
        # Log response details
        duration = time.time() - start_time
        logger.info(
            f"Request completed: {response.status_code} - {duration:.3f}s"
        )
        
        # Add response time header
        response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def process_exception(self, request, exception):
        """Log exceptions that occur during request processing."""
        logger.error(
            f"Exception in {request.method} {request.path}: {exception}",
            exc_info=True
        )
        return None  # Let Django handle the exception