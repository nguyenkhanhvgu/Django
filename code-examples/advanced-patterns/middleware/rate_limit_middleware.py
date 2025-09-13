"""
Rate limiting middleware example.
"""
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import time
import json

class RateLimitMiddleware:
    """
    Middleware to implement rate limiting based on client IP.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'RATE_LIMIT_REQUESTS_PER_MINUTE', 100)
        self.window = 60  # seconds

    def __call__(self, request):
        # Skip rate limiting for admin and static files
        if self.should_skip_rate_limiting(request):
            return self.get_response(request)
        
        client_ip = self.get_client_ip(request)
        
        if self.is_rate_limited(client_ip):
            return self.rate_limit_response(request)
        
        response = self.get_response(request)
        
        # Add rate limit headers
        remaining_requests = self.get_remaining_requests(client_ip)
        response['X-RateLimit-Limit'] = str(self.rate_limit)
        response['X-RateLimit-Remaining'] = str(remaining_requests)
        response['X-RateLimit-Reset'] = str(int(time.time()) + self.window)
        
        return response
    
    def should_skip_rate_limiting(self, request):
        """Determine if rate limiting should be skipped for this request."""
        skip_paths = ['/admin/', '/static/', '/media/']
        return any(request.path.startswith(path) for path in skip_paths)
    
    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, client_ip):
        """Check if the client IP is rate limited."""
        cache_key = f"rate_limit_{client_ip}"
        
        # Get current request timestamps
        requests = cache.get(cache_key, [])
        now = time.time()
        
        # Remove old requests outside the window
        requests = [req_time for req_time in requests if now - req_time < self.window]
        
        # Check if rate limit exceeded
        if len(requests) >= self.rate_limit:
            return True
        
        # Add current request
        requests.append(now)
        cache.set(cache_key, requests, self.window)
        
        return False
    
    def get_remaining_requests(self, client_ip):
        """Get the number of remaining requests for the client IP."""
        cache_key = f"rate_limit_{client_ip}"
        requests = cache.get(cache_key, [])
        now = time.time()
        
        # Count requests within the window
        recent_requests = [req_time for req_time in requests if now - req_time < self.window]
        return max(0, self.rate_limit - len(recent_requests))
    
    def rate_limit_response(self, request):
        """Return appropriate response when rate limit is exceeded."""
        if request.content_type == 'application/json' or request.path.startswith('/api/'):
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {self.rate_limit} requests per minute allowed'
                },
                status=429
            )
        else:
            return HttpResponse(
                "Rate limit exceeded. Please try again later.",
                status=429,
                content_type='text/plain'
            )