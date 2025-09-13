# Microservices Architecture with Django

import json
import requests
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Service Registry Pattern
class ServiceRegistry:
    """
    Central registry for microservice discovery
    """
    
    def __init__(self):
        self.services = {}
    
    def register_service(self, name: str, host: str, port: int, health_check_url: str = None):
        """Register a service with the registry"""
        self.services[name] = {
            'host': host,
            'port': port,
            'url': f"http://{host}:{port}",
            'health_check_url': health_check_url or f"http://{host}:{port}/health/",
            'status': 'healthy',
            'last_check': None
        }
        logger.info(f"Registered service: {name} at {host}:{port}")
    
    def get_service(self, name: str) -> Optional[Dict]:
        """Get service information by name"""
        return self.services.get(name)
    
    def get_service_url(self, name: str) -> Optional[str]:
        """Get service URL by name"""
        service = self.get_service(name)
        return service['url'] if service else None
    
    def list_services(self) -> Dict[str, Dict]:
        """List all registered services"""
        return self.services.copy()
    
    def deregister_service(self, name: str):
        """Remove service from registry"""
        if name in self.services:
            del self.services[name]
            logger.info(f"Deregistered service: {name}")

# Global service registry instance
service_registry = ServiceRegistry()

# Service Communication Patterns
class ServiceClient:
    """
    Base client for inter-service communication
    """
    
    def __init__(self, service_name: str, timeout: int = 30):
        self.service_name = service_name
        self.timeout = timeout
        self.base_url = service_registry.get_service_url(service_name)
        
        if not self.base_url:
            raise ValueError(f"Service {service_name} not found in registry")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request to service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to {self.service_name} failed: {e}")
            raise ServiceCommunicationError(f"Failed to communicate with {self.service_name}: {e}")
    
    def get(self, endpoint: str, params: Dict = None) -> Dict:
        """Make GET request"""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Dict = None) -> Dict:
        """Make POST request"""
        return self._make_request('POST', endpoint, data=data)
    
    def put(self, endpoint: str, data: Dict = None) -> Dict:
        """Make PUT request"""
        return self._make_request('PUT', endpoint, data=data)
    
    def delete(self, endpoint: str) -> Dict:
        """Make DELETE request"""
        return self._make_request('DELETE', endpoint)

# Async service client for better performance
class AsyncServiceClient:
    """
    Async client for non-blocking inter-service communication
    """
    
    def __init__(self, service_name: str, timeout: int = 30):
        self.service_name = service_name
        self.timeout = timeout
        self.base_url = service_registry.get_service_url(service_name)
        
        if not self.base_url:
            raise ValueError(f"Service {service_name} not found in registry")
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make async HTTP request to service"""
        url = f"{self.base_url}{endpoint}"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            
            except aiohttp.ClientError as e:
                logger.error(f"Async request to {self.service_name} failed: {e}")
                raise ServiceCommunicationError(f"Failed to communicate with {self.service_name}: {e}")
    
    async def get(self, endpoint: str, params: Dict = None) -> Dict:
        """Make async GET request"""
        return await self._make_request('GET', endpoint, params=params)
    
    async def post(self, endpoint: str, data: Dict = None) -> Dict:
        """Make async POST request"""
        return await self._make_request('POST', endpoint, data=data)

# Custom exceptions
class ServiceCommunicationError(Exception):
    """Exception raised when service communication fails"""
    pass

class ServiceUnavailableError(Exception):
    """Exception raised when service is unavailable"""
    pass

# Event-driven communication
@dataclass
class Event:
    id: str
    type: str
    source: str
    data: Dict[str, Any]
    timestamp: str

class EventBus:
    """
    Simple event bus for microservices communication
    """
    
    def __init__(self):
        self.subscribers = {}
        self.channel = None  # Would be replaced with actual message broker
    
    def subscribe(self, event_pattern: str, callback):
        """Subscribe to events matching pattern"""
        if event_pattern not in self.subscribers:
            self.subscribers[event_pattern] = []
        
        self.subscribers[event_pattern].append(callback)
    
    def publish(self, event: Event):
        """Publish event to subscribers"""
        # In real implementation, this would use a message broker like RabbitMQ or Kafka
        routing_key = f"{event.source}.{event.type}"
        
        # Find matching subscribers
        for pattern, callbacks in self.subscribers.items():
            if self._pattern_matches(pattern, routing_key):
                for callback in callbacks:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"Error processing event {event.id}: {e}")
    
    def _pattern_matches(self, pattern: str, routing_key: str) -> bool:
        """Simple pattern matching (would be more sophisticated in real implementation)"""
        return pattern == routing_key or pattern == '*' or pattern.endswith('*') and routing_key.startswith(pattern[:-1])

# Global event bus
event_bus = EventBus()

# Microservice base class
class MicroService:
    """
    Base class for Django microservices
    """
    
    def __init__(self, name: str, host: str = 'localhost', port: int = 8000):
        self.name = name
        self.host = host
        self.port = port
        self.dependencies = []
        
        # Register with service registry
        service_registry.register_service(name, host, port)
    
    def add_dependency(self, service_name: str):
        """Add service dependency"""
        self.dependencies.append(service_name)
    
    def get_client(self, service_name: str) -> ServiceClient:
        """Get client for communicating with another service"""
        return ServiceClient(service_name)
    
    def get_async_client(self, service_name: str) -> AsyncServiceClient:
        """Get async client for communicating with another service"""
        return AsyncServiceClient(service_name)
    
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            'service': self.name,
            'status': 'healthy',
            'dependencies': self._check_dependencies()
        }
    
    def _check_dependencies(self) -> Dict[str, str]:
        """Check health of service dependencies"""
        dependency_status = {}
        
        for dep in self.dependencies:
            try:
                client = ServiceClient(dep, timeout=5)
                client.get('/health/')
                dependency_status[dep] = 'healthy'
            except Exception:
                dependency_status[dep] = 'unhealthy'
        
        return dependency_status

# Example microservices

# User Service
class UserService(MicroService):
    """
    User management microservice
    """
    
    def __init__(self):
        super().__init__('user-service', port=8001)
    
    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        # User creation logic
        user = {
            'id': user_data.get('id'),
            'username': user_data.get('username'),
            'email': user_data.get('email'),
            'created_at': '2023-01-01T00:00:00Z'
        }
        
        # Publish user created event
        event = Event(
            id=f"user-{user['id']}-created",
            type='user.created',
            source='user-service',
            data=user,
            timestamp='2023-01-01T00:00:00Z'
        )
        event_bus.publish(event)
        
        return user
    
    def get_user(self, user_id: int) -> Dict:
        """Get user by ID"""
        # User retrieval logic
        return {
            'id': user_id,
            'username': f'user{user_id}',
            'email': f'user{user_id}@example.com'
        }

# Order Service
class OrderService(MicroService):
    """
    Order management microservice
    """
    
    def __init__(self):
        super().__init__('order-service', port=8002)
        self.add_dependency('user-service')
        self.add_dependency('inventory-service')
        self.add_dependency('payment-service')
    
    def create_order(self, order_data: Dict) -> Dict:
        """Create a new order with dependency calls"""
        user_id = order_data.get('user_id')
        items = order_data.get('items', [])
        
        try:
            # Verify user exists
            user_client = self.get_client('user-service')
            user = user_client.get(f'/users/{user_id}/')
            
            # Check inventory
            inventory_client = self.get_client('inventory-service')
            for item in items:
                inventory_client.post('/inventory/reserve/', {
                    'product_id': item['product_id'],
                    'quantity': item['quantity']
                })
            
            # Process payment
            payment_client = self.get_client('payment-service')
            payment_result = payment_client.post('/payments/', {
                'user_id': user_id,
                'amount': order_data.get('total_amount'),
                'currency': 'USD'
            })
            
            # Create order
            order = {
                'id': order_data.get('id'),
                'user_id': user_id,
                'items': items,
                'total_amount': order_data.get('total_amount'),
                'status': 'confirmed',
                'payment_id': payment_result.get('id')
            }
            
            # Publish order created event
            event = Event(
                id=f"order-{order['id']}-created",
                type='order.created',
                source='order-service',
                data=order,
                timestamp='2023-01-01T00:00:00Z'
            )
            event_bus.publish(event)
            
            return order
            
        except ServiceCommunicationError as e:
            logger.error(f"Failed to create order: {e}")
            # Implement compensation logic here
            raise

# Notification Service
class NotificationService(MicroService):
    """
    Notification microservice that responds to events
    """
    
    def __init__(self):
        super().__init__('notification-service', port=8003)
        
        # Subscribe to events
        event_bus.subscribe('user.created', self.handle_user_created)
        event_bus.subscribe('order.created', self.handle_order_created)
    
    def handle_user_created(self, event: Event):
        """Handle user created event"""
        user_data = event.data
        
        # Send welcome email
        self.send_email(
            to_email=user_data['email'],
            subject='Welcome!',
            body=f"Welcome {user_data['username']}!"
        )
    
    def handle_order_created(self, event: Event):
        """Handle order created event"""
        order_data = event.data
        
        # Get user info
        user_client = self.get_client('user-service')
        user = user_client.get(f"/users/{order_data['user_id']}/")
        
        # Send order confirmation
        self.send_email(
            to_email=user['email'],
            subject='Order Confirmation',
            body=f"Your order #{order_data['id']} has been confirmed!"
        )
    
    def send_email(self, to_email: str, subject: str, body: str):
        """Send email notification"""
        # Email sending logic
        logger.info(f"Sending email to {to_email}: {subject}")

# API Gateway pattern
class APIGateway:
    """
    API Gateway for routing requests to microservices
    """
    
    def __init__(self):
        self.routes = {}
        self.middleware = []
    
    def add_route(self, path_prefix: str, service_name: str):
        """Add route mapping"""
        self.routes[path_prefix] = service_name
    
    def add_middleware(self, middleware_func):
        """Add middleware function"""
        self.middleware.append(middleware_func)
    
    def route_request(self, request_path: str, method: str, data: Dict = None) -> Dict:
        """Route request to appropriate microservice"""
        # Apply middleware
        for middleware_func in self.middleware:
            result = middleware_func(request_path, method, data)
            if result:  # Middleware can block request
                return result
        
        # Find matching service
        service_name = None
        for prefix, svc_name in self.routes.items():
            if request_path.startswith(prefix):
                service_name = svc_name
                break
        
        if not service_name:
            return {'error': 'Service not found', 'status': 404}
        
        # Forward request to service
        try:
            client = ServiceClient(service_name)
            
            # Remove prefix from path
            service_path = request_path
            for prefix in self.routes:
                if request_path.startswith(prefix):
                    service_path = request_path[len(prefix):]
                    break
            
            if method == 'GET':
                return client.get(service_path)
            elif method == 'POST':
                return client.post(service_path, data)
            elif method == 'PUT':
                return client.put(service_path, data)
            elif method == 'DELETE':
                return client.delete(service_path)
            
        except ServiceCommunicationError as e:
            return {'error': str(e), 'status': 503}

# Circuit breaker for resilient communication
class CircuitBreaker:
    """
    Circuit breaker pattern for microservice communication
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise ServiceUnavailableError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        import time
        return time.time() - self.last_failure_time > self.timeout
    
    def _on_success(self):
        """Reset circuit breaker on successful call"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Handle failure and potentially open circuit"""
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

# Django views for microservice endpoints
@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'django-microservice',
        'timestamp': '2023-01-01T00:00:00Z'
    })

@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):
    """Create user endpoint"""
    try:
        data = json.loads(request.body)
        user_service = UserService()
        user = user_service.create_user(data)
        return JsonResponse(user, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def create_order(request):
    """Create order endpoint"""
    try:
        data = json.loads(request.body)
        order_service = OrderService()
        order = order_service.create_order(data)
        return JsonResponse(order, status=201)
    except ServiceCommunicationError as e:
        return JsonResponse({'error': str(e)}, status=503)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Usage example
if __name__ == "__main__":
    # Initialize services
    user_service = UserService()
    order_service = OrderService()
    notification_service = NotificationService()
    
    # Setup API Gateway
    gateway = APIGateway()
    gateway.add_route('/api/users/', 'user-service')
    gateway.add_route('/api/orders/', 'order-service')
    gateway.add_route('/api/notifications/', 'notification-service')
    
    # Example usage
    user_data = {
        'id': 1,
        'username': 'john_doe',
        'email': 'john@example.com'
    }
    
    order_data = {
        'id': 1,
        'user_id': 1,
        'items': [
            {'product_id': 1, 'quantity': 2},
            {'product_id': 2, 'quantity': 1}
        ],
        'total_amount': 99.99
    }
    
    # Create user and order
    user = user_service.create_user(user_data)
    print(f"Created user: {user}")
    
    # This would trigger notifications via event bus
    order = order_service.create_order(order_data)
    print(f"Created order: {order}")