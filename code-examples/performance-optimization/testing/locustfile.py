"""
Locust Load Testing Configuration for Django Applications

This file contains comprehensive load testing scenarios for Django applications,
including authentication, CRUD operations, and API testing.
"""

from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask
import random
import json
import time
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DjangoWebUser(HttpUser):
    """
    Simulates a typical web user interacting with a Django application
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts - perform login"""
        self.login()
        self.csrf_token = self.get_csrf_token()
    
    def login(self):
        """Authenticate user"""
        # Get login page to retrieve CSRF token
        response = self.client.get("/login/")
        if response.status_code != 200:
            logger.error(f"Failed to get login page: {response.status_code}")
            return
        
        # Extract CSRF token (simplified - in real app, parse HTML)
        csrf_token = self.get_csrf_token_from_response(response)
        
        # Perform login
        login_data = {
            'username': f'testuser_{random.randint(1, 1000)}',
            'password': 'testpassword123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        response = self.client.post(
            "/login/",
            data=login_data,
            headers={'Referer': self.client.base_url + '/login/'}
        )
        
        if response.status_code == 200 and 'dashboard' in response.url:
            logger.info("Login successful")
        else:
            logger.warning(f"Login may have failed: {response.status_code}")
    
    def get_csrf_token(self):
        """Get CSRF token from Django"""
        response = self.client.get("/")
        # In a real implementation, you'd parse the HTML to extract the token
        return "dummy_csrf_token"
    
    def get_csrf_token_from_response(self, response):
        """Extract CSRF token from response (simplified)"""
        # In real implementation, parse HTML to find csrf token
        return "dummy_csrf_token"
    
    @task(3)
    def view_homepage(self):
        """Visit the homepage - most common action"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Homepage returned {response.status_code}")
    
    @task(5)
    def view_post_list(self):
        """View list of blog posts"""
        with self.client.get("/posts/", catch_response=True) as response:
            if response.status_code == 200:
                if "posts" in response.text.lower():
                    response.success()
                else:
                    response.failure("Posts page doesn't contain expected content")
            else:
                response.failure(f"Posts list returned {response.status_code}")
    
    @task(2)
    def view_post_detail(self):
        """View individual post details"""
        post_id = random.randint(1, 100)  # Assume posts with IDs 1-100 exist
        
        with self.client.get(f"/posts/{post_id}/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # 404 is acceptable for random post IDs
                response.success()
            else:
                response.failure(f"Post detail returned {response.status_code}")
    
    @task(1)
    def create_post(self):
        """Create a new blog post"""
        post_data = {
            'title': f'Test Post {random.randint(1, 10000)}',
            'content': f'This is test content created at {time.time()}',
            'category': random.choice(['tech', 'lifestyle', 'news']),
            'csrfmiddlewaretoken': self.csrf_token
        }
        
        with self.client.post("/posts/create/", data=post_data, catch_response=True) as response:
            if response.status_code in [200, 201, 302]:  # Success or redirect
                response.success()
            else:
                response.failure(f"Post creation returned {response.status_code}")
    
    @task(1)
    def search_posts(self):
        """Search for posts"""
        search_terms = ['django', 'python', 'web', 'development', 'tutorial']
        search_query = random.choice(search_terms)
        
        with self.client.get(f"/search/?q={search_query}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Search returned {response.status_code}")
    
    @task(1)
    def view_user_profile(self):
        """View user profile"""
        with self.client.get("/profile/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 302:  # Redirect to login
                response.success()
            else:
                response.failure(f"Profile view returned {response.status_code}")


class DjangoAPIUser(HttpUser):
    """
    Simulates API client interacting with Django REST API
    """
    wait_time = between(0.5, 2)
    
    def on_start(self):
        """Authenticate with API"""
        self.authenticate_api()
    
    def authenticate_api(self):
        """Get API authentication token"""
        auth_data = {
            'username': f'apiuser_{random.randint(1, 100)}',
            'password': 'apipassword123'
        }
        
        response = self.client.post("/api/auth/login/", json=auth_data)
        
        if response.status_code == 200:
            token = response.json().get('token')
            if token:
                self.client.headers.update({'Authorization': f'Bearer {token}'})
                logger.info("API authentication successful")
            else:
                logger.warning("No token received from API auth")
        else:
            logger.error(f"API authentication failed: {response.status_code}")
    
    @task(4)
    def get_posts_api(self):
        """Get posts via API"""
        with self.client.get("/api/posts/", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, (list, dict)):
                        response.success()
                    else:
                        response.failure("Invalid JSON response")
                except json.JSONDecodeError:
                    response.failure("Response is not valid JSON")
            else:
                response.failure(f"API posts returned {response.status_code}")
    
    @task(2)
    def get_post_detail_api(self):
        """Get individual post via API"""
        post_id = random.randint(1, 100)
        
        with self.client.get(f"/api/posts/{post_id}/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # 404 is acceptable
            else:
                response.failure(f"API post detail returned {response.status_code}")
    
    @task(1)
    def create_post_api(self):
        """Create post via API"""
        post_data = {
            'title': f'API Test Post {random.randint(1, 10000)}',
            'content': f'API content created at {time.time()}',
            'category': random.choice(['tech', 'lifestyle', 'news']),
            'published': True
        }
        
        with self.client.post("/api/posts/", json=post_data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"API post creation returned {response.status_code}")
    
    @task(1)
    def update_post_api(self):
        """Update post via API"""
        post_id = random.randint(1, 50)  # Update existing posts
        update_data = {
            'title': f'Updated Post {post_id} at {time.time()}',
            'content': 'Updated content'
        }
        
        with self.client.patch(f"/api/posts/{post_id}/", json=update_data, catch_response=True) as response:
            if response.status_code in [200, 404]:  # 404 acceptable for non-existent posts
                response.success()
            else:
                response.failure(f"API post update returned {response.status_code}")


class HeavyLoadUser(HttpUser):
    """
    Simulates heavy load scenarios for stress testing
    """
    wait_time = between(0.1, 0.5)  # Very short wait times
    
    @task(10)
    def rapid_homepage_requests(self):
        """Rapid homepage requests"""
        self.client.get("/")
    
    @task(5)
    def rapid_api_requests(self):
        """Rapid API requests"""
        self.client.get("/api/posts/")
    
    @task(3)
    def concurrent_database_operations(self):
        """Operations that hit the database hard"""
        # Search (typically database-intensive)
        self.client.get("/search/?q=test")
        
        # Complex filtering
        self.client.get("/posts/?category=tech&sort=popular")
    
    @task(1)
    def memory_intensive_operations(self):
        """Operations that use more memory"""
        # Request large datasets
        self.client.get("/api/posts/?limit=1000")


# Custom event handlers for detailed monitoring
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Log slow requests"""
    if response_time > 2000:  # Log requests slower than 2 seconds
        logger.warning(f"Slow request: {request_type} {name} took {response_time}ms")


@events.user_error.add_listener
def on_user_error(user_instance, exception, tb, **kwargs):
    """Log user errors"""
    logger.error(f"User error: {exception}")


# Test scenarios for different load patterns
class MorningTrafficUser(HttpUser):
    """Simulates morning traffic pattern - mostly reading"""
    wait_time = between(2, 5)
    weight = 3  # Higher weight = more users of this type
    
    @task(8)
    def read_content(self):
        self.client.get("/posts/")
    
    @task(2)
    def light_interaction(self):
        self.client.get("/search/?q=news")


class EveningTrafficUser(HttpUser):
    """Simulates evening traffic - more interaction"""
    wait_time = between(1, 3)
    weight = 2
    
    @task(5)
    def read_content(self):
        self.client.get("/posts/")
    
    @task(3)
    def interact(self):
        self.client.post("/posts/1/like/")
    
    @task(2)
    def create_content(self):
        post_data = {
            'title': f'Evening Post {random.randint(1, 1000)}',
            'content': 'Evening content'
        }
        self.client.post("/posts/create/", data=post_data)


# Performance test configuration
class PerformanceTestConfig:
    """Configuration for different performance test scenarios"""
    
    SCENARIOS = {
        'light_load': {
            'users': 10,
            'spawn_rate': 2,
            'duration': '5m'
        },
        'normal_load': {
            'users': 50,
            'spawn_rate': 5,
            'duration': '10m'
        },
        'heavy_load': {
            'users': 200,
            'spawn_rate': 10,
            'duration': '15m'
        },
        'stress_test': {
            'users': 500,
            'spawn_rate': 20,
            'duration': '20m'
        },
        'spike_test': {
            'users': 1000,
            'spawn_rate': 50,
            'duration': '5m'
        }
    }
    
    @classmethod
    def get_scenario(cls, scenario_name):
        """Get configuration for a specific scenario"""
        return cls.SCENARIOS.get(scenario_name, cls.SCENARIOS['normal_load'])


# Usage examples:
# 
# Basic load test:
# locust -f locustfile.py --host=http://localhost:8000
#
# Specific user class:
# locust -f locustfile.py --host=http://localhost:8000 DjangoAPIUser
#
# Headless mode with specific parameters:
# locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 5m --headless
#
# Multiple user types:
# locust -f locustfile.py --host=http://localhost:8000 MorningTrafficUser EveningTrafficUser