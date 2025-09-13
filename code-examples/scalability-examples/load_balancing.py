# Load Balancer Configuration Examples

# Nginx configuration for Django load balancing
NGINX_CONFIG = """
upstream django_app {
    least_conn;
    server 10.0.1.10:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 weight=2 max_fails=3 fail_timeout=30s;
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
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/media/;
        expires 30d;
    }
}
"""

# HAProxy configuration
HAPROXY_CONFIG = """
global
    daemon
    maxconn 4096

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend django_frontend
    bind *:443 ssl crt /path/to/certificate.pem
    default_backend django_backend

backend django_backend
    balance roundrobin
    option httpchk GET /health/
    server django1 10.0.1.10:8000 check
    server django2 10.0.1.11:8000 check
    server django3 10.0.1.12:8000 check
"""

# Application-level load balancing
import random
import time
from typing import List, Dict
from collections import defaultdict

class ApplicationLoadBalancer:
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.current = 0
        self.weights = {server: 1 for server in servers}
        self.connections = defaultdict(int)
        self.response_times = defaultdict(list)
    
    def round_robin(self) -> str:
        """Simple round-robin load balancing"""
        server = self.servers[self.current % len(self.servers)]
        self.current += 1
        return server
    
    def weighted_random(self) -> str:
        """Weighted random selection based on server capacity"""
        weighted_servers = []
        for server, weight in self.weights.items():
            weighted_servers.extend([server] * weight)
        return random.choice(weighted_servers)
    
    def least_connections(self) -> str:
        """Route to server with least active connections"""
        return min(self.servers, key=lambda s: self.connections[s])
    
    def least_response_time(self) -> str:
        """Route to server with best average response time"""
        def avg_response_time(server):
            times = self.response_times[server]
            return sum(times) / len(times) if times else float('inf')
        
        return min(self.servers, key=avg_response_time)
    
    def health_aware_routing(self) -> str:
        """Route only to healthy servers"""
        healthy_servers = [s for s in self.servers if self._is_healthy(s)]
        if not healthy_servers:
            raise Exception("No healthy servers available")
        
        # Use least connections among healthy servers
        return min(healthy_servers, key=lambda s: self.connections[s])
    
    def _is_healthy(self, server: str) -> bool:
        """Check if server is healthy (simplified implementation)"""
        # In real implementation, this would make actual health checks
        return True
    
    def record_response_time(self, server: str, response_time: float):
        """Record response time for adaptive load balancing"""
        self.response_times[server].append(response_time)
        # Keep only last 100 measurements
        if len(self.response_times[server]) > 100:
            self.response_times[server] = self.response_times[server][-100:]
    
    def increment_connections(self, server: str):
        """Track active connections"""
        self.connections[server] += 1
    
    def decrement_connections(self, server: str):
        """Track connection completion"""
        self.connections[server] = max(0, self.connections[server] - 1)

# Usage example
load_balancer = ApplicationLoadBalancer([
    'http://django-1:8000',
    'http://django-2:8000',
    'http://django-3:8000'
])

# Different load balancing strategies
selected_server = load_balancer.round_robin()
print(f"Round robin selected: {selected_server}")

selected_server = load_balancer.least_connections()
print(f"Least connections selected: {selected_server}")

selected_server = load_balancer.health_aware_routing()
print(f"Health-aware selected: {selected_server}")

# Session affinity (sticky sessions) implementation
class StickySessionBalancer:
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.session_map = {}
    
    def get_server_for_session(self, session_id: str) -> str:
        """Route requests to same server based on session ID"""
        if session_id not in self.session_map:
            # Hash session ID to consistently select server
            server_index = hash(session_id) % len(self.servers)
            self.session_map[session_id] = self.servers[server_index]
        
        return self.session_map[session_id]
    
    def remove_session(self, session_id: str):
        """Clean up session mapping"""
        self.session_map.pop(session_id, None)

# Circuit breaker pattern for resilient load balancing
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Reset circuit breaker on successful call"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Handle failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'

# Load balancer with circuit breaker
class ResilientLoadBalancer:
    def __init__(self, servers: List[str]):
        self.servers = servers
        self.circuit_breakers = {
            server: CircuitBreaker() for server in servers
        }
        self.base_balancer = ApplicationLoadBalancer(servers)
    
    def get_server(self) -> str:
        """Get server with circuit breaker protection"""
        available_servers = []
        
        for server in self.servers:
            if self.circuit_breakers[server].state != 'OPEN':
                available_servers.append(server)
        
        if not available_servers:
            raise Exception("All servers are unavailable")
        
        # Use base load balancer logic on available servers
        temp_balancer = ApplicationLoadBalancer(available_servers)
        return temp_balancer.least_connections()
    
    def record_request_result(self, server: str, success: bool, response_time: float = None):
        """Record request result for circuit breaker and load balancing"""
        if success:
            self.circuit_breakers[server]._on_success()
            if response_time:
                self.base_balancer.record_response_time(server, response_time)
        else:
            self.circuit_breakers[server]._on_failure()