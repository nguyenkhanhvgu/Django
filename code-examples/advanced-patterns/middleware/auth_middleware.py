"""
API authentication middleware example.
"""
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger('middleware')

class APIAuthenticationMiddleware:
    """
    Middleware to handle API key authentication for API endpoints.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.api_key = getattr(settings, 'API_KEY', 'your-secret-api-key')

    def __call__(self, request):
        # Only apply to API endpoints
        if not self.is_api_request(request):
            return self.get_response(request)
        
        # Skip authentication for public API endpoints
        if self.is_public_api_endpoint(request):
            return self.get_response(request)
        
        # Check for API key
        api_key = self.get_api_key_from_request(request)
        
        if not api_key:
            logger.warning(f"API request without key: {request.path}")
            return JsonResponse(
                {'error': 'API key required', 'message': 'Include X-API-Key header'},
                status=401
            )
        
        if not self.validate_api_key(api_key):
            logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
            return JsonResponse(
                {'error': 'Invalid API key'},
                status=401
            )
        
        # Add API key info to request for logging
        request.api_authenticated = True
        request.api_key = api_key
        
        response = self.get_response(request)
        
        # Add API-specific headers
        response['X-API-Version'] = '1.0'
        response['X-API-Authenticated'] = 'true'
        
        return response
    
    def is_api_request(self, request):
        """Check if this is an API request."""
        return (
            request.path.startswith('/api/') or
            request.content_type == 'application/json' or
            'application/json' in request.META.get('HTTP_ACCEPT', '')
        )
    
    def is_public_api_endpoint(self, request):
        """Check if this is a public API endpoint that doesn't require authentication."""
        public_endpoints = [
            '/api/public/',
            '/api/health/',
            '/api/docs/',
        ]
        return any(request.path.startswith(endpoint) for endpoint in public_endpoints)
    
    def get_api_key_from_request(self, request):
        """Extract API key from request headers or query parameters."""
        # Try header first (preferred method)
        api_key = request.META.get('HTTP_X_API_KEY')
        
        # Fallback to query parameter (less secure)
        if not api_key:
            api_key = request.GET.get('api_key')
        
        return api_key
    
    def validate_api_key(self, api_key):
        """
        Validate the provided API key.
        In a real application, this would check against a database.
        """
        # Simple validation for demo purposes
        return api_key == self.api_key
    
    def process_exception(self, request, exception):
        """Handle exceptions in API requests."""
        if hasattr(request, 'api_authenticated') and request.api_authenticated:
            logger.error(f"API exception in {request.path}: {exception}")
        return None