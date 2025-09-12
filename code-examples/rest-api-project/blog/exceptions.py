"""
Custom exception handlers for the blog API.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Log the exception
        logger.error(f"API Exception: {exc}", exc_info=True, extra={
            'request': context.get('request'),
            'view': context.get('view'),
        })
        
        # Get the standard error response
        standard_error_response = response.data
        
        # Create custom error response format
        custom_response_data = {
            'error': {
                'status_code': response.status_code,
                'message': get_error_message(response.status_code),
                'details': standard_error_response,
                'timestamp': get_current_timestamp(),
            }
        }
        
        # Add request information for debugging (only in development)
        if hasattr(context.get('request'), 'user'):
            request = context['request']
            custom_response_data['error']['request_info'] = {
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
            }
        
        response.data = custom_response_data
    
    return response


def get_error_message(status_code):
    """
    Get a user-friendly error message based on status code.
    """
    error_messages = {
        400: "Bad Request - The request could not be understood or was missing required parameters.",
        401: "Unauthorized - Authentication failed or user doesn't have permissions for requested operation.",
        403: "Forbidden - Access denied. You don't have permission to access this resource.",
        404: "Not Found - The requested resource could not be found.",
        405: "Method Not Allowed - The request method is not supported for this resource.",
        406: "Not Acceptable - The requested resource is not available in a format acceptable by your browser.",
        409: "Conflict - The request could not be completed due to a conflict with the current state of the resource.",
        410: "Gone - The requested resource is no longer available and will not be available again.",
        422: "Unprocessable Entity - The request was well-formed but was unable to be followed due to semantic errors.",
        429: "Too Many Requests - Rate limit exceeded. Please try again later.",
        500: "Internal Server Error - An error occurred on the server.",
        502: "Bad Gateway - The server received an invalid response from an upstream server.",
        503: "Service Unavailable - The server is currently unavailable (overloaded or down).",
        504: "Gateway Timeout - The server did not receive a timely response from an upstream server.",
    }
    
    return error_messages.get(status_code, "An error occurred while processing your request.")


def get_current_timestamp():
    """
    Get current timestamp in ISO format.
    """
    from django.utils import timezone
    return timezone.now().isoformat()


class APIException(Exception):
    """
    Base class for custom API exceptions.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "An error occurred"
    
    def __init__(self, message=None, status_code=None):
        self.message = message or self.default_message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIException):
    """
    Custom validation error.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Validation failed"


class AuthenticationError(APIException):
    """
    Custom authentication error.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Authentication failed"


class PermissionError(APIException):
    """
    Custom permission error.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "Permission denied"


class NotFoundError(APIException):
    """
    Custom not found error.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Resource not found"


class ConflictError(APIException):
    """
    Custom conflict error.
    """
    status_code = status.HTTP_409_CONFLICT
    default_message = "Resource conflict"


class RateLimitError(APIException):
    """
    Custom rate limit error.
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_message = "Rate limit exceeded"


# Custom exception handlers for specific cases
def handle_database_error(exc, context):
    """
    Handle database-related errors.
    """
    logger.error(f"Database error: {exc}", exc_info=True)
    
    return Response({
        'error': {
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': "A database error occurred. Please try again later.",
            'timestamp': get_current_timestamp(),
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def handle_validation_error(exc, context):
    """
    Handle validation errors with detailed field information.
    """
    errors = {}
    
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            for field, messages in exc.detail.items():
                if isinstance(messages, list):
                    errors[field] = [str(msg) for msg in messages]
                else:
                    errors[field] = [str(messages)]
        else:
            errors['non_field_errors'] = [str(exc.detail)]
    
    return Response({
        'error': {
            'status_code': status.HTTP_400_BAD_REQUEST,
            'message': "Validation failed",
            'field_errors': errors,
            'timestamp': get_current_timestamp(),
        }
    }, status=status.HTTP_400_BAD_REQUEST)


def handle_permission_denied(exc, context):
    """
    Handle permission denied errors with helpful messages.
    """
    user = context.get('request').user if context.get('request') else None
    
    message = "You don't have permission to perform this action."
    
    if not user or not user.is_authenticated:
        message = "Authentication required to perform this action."
    
    return Response({
        'error': {
            'status_code': status.HTTP_403_FORBIDDEN,
            'message': message,
            'timestamp': get_current_timestamp(),
        }
    }, status=status.HTTP_403_FORBIDDEN)