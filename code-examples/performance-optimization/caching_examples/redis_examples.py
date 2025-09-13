"""
Redis Caching Examples for Django

This module demonstrates various Redis caching patterns and strategies
for Django applications, including basic caching, advanced patterns,
and cache invalidation strategies.
"""

import json
import time
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django_redis import get_redis_connection
import redis


class RedisCache:
    """Advanced Redis caching utility class"""
    
    def __init__(self, connection_alias='default'):
        self.connection_alias = connection_alias
        self.redis_conn = get_redis_connection(connection_alias)
    
    def get_or_set_json(self, key, callable_func, timeout=3600):
        """Cache with JSON serialization for complex objects"""
        data = cache.get(key)
        if data is None:
            data = callable_func()
            # Serialize complex objects
            serialized_data = json.dumps(data, cls=DjangoJSONEncoder)
            cache.set(key, serialized_data, timeout)
            return data
        return json.loads(data)
    
    def set_with_tags(self, key, value, timeout=3600, tags=None):
        """Set cache with tags for group invalidation"""
        cache.set(key, value, timeout)
        
        if tags:
            for tag in tags:
                tag_key = f"tag:{tag}"
                # Add key to tag set
                self.redis_conn.sadd(tag_key, key)
                # Set expiration for tag
                self.redis_conn.expire(tag_key, timeout + 300)  # Tag lives longer
    
    def invalidate_by_tag(self, tag):
        """Invalidate all cache keys associated with a tag"""
        tag_key = f"tag:{tag}"
        keys = self.redis_conn.smembers(tag_key)
        
        if keys:
            # Delete all keys associated with the tag
            cache.delete_many([key.decode() for key in keys])
            # Delete the tag itself
            self.redis_conn.delete(tag_key)
    
    def invalidate_pattern(self, pattern):
        """Invalidate cache keys matching a pattern"""
        keys = self.redis_conn.keys(pattern)
        if keys:
            self.redis_conn.delete(*keys)
    
    def get_cache_stats(self):
        """Get Redis cache statistics"""
        info = self.redis_conn.info()
        return {
            'used_memory': info.get('used_memory_human'),
            'connected_clients': info.get('connected_clients'),
            'total_commands_processed': info.get('total_commands_processed'),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'hit_rate': self._calculate_hit_rate(
                info.get('keyspace_hits', 0),
                info.get('keyspace_misses', 0)
            )
        }
    
    def _calculate_hit_rate(self, hits, misses):
        """Calculate cache hit rate percentage"""
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0


# Initialize Redis cache utility
redis_cache = RedisCache()


def basic_caching_example():
    """Demonstrate basic Redis caching operations"""
    print("=== Basic Redis Caching Example ===")
    
    # Simple key-value caching
    cache_key = 'user_profile_123'
    user_data = {
        'id': 123,
        'name': 'John Doe',
        'email': 'john@example.com',
        'preferences': {'theme': 'dark', 'notifications': True}
    }
    
    # Set cache
    cache.set(cache_key, user_data, timeout=3600)  # 1 hour
    print(f"Cached user data: {cache_key}")
    
    # Get from cache
    cached_data = cache.get(cache_key)
    print(f"Retrieved from cache: {cached_data}")
    
    # Check if key exists
    if cache.has_key(cache_key):
        print(f"Key {cache_key} exists in cache")
    
    # Delete from cache
    cache.delete(cache_key)
    print(f"Deleted key: {cache_key}")


def advanced_caching_patterns():
    """Demonstrate advanced Redis caching patterns"""
    print("\n=== Advanced Caching Patterns ===")
    
    # 1. Cache-aside pattern
    def get_user_posts(user_id):
        cache_key = f'user_posts_{user_id}'
        posts = cache.get(cache_key)
        
        if posts is None:
            # Simulate database query
            posts = [
                {'id': 1, 'title': 'Post 1', 'content': 'Content 1'},
                {'id': 2, 'title': 'Post 2', 'content': 'Content 2'},
            ]
            cache.set(cache_key, posts, timeout=1800)  # 30 minutes
            print(f"Loaded posts from database for user {user_id}")
        else:
            print(f"Loaded posts from cache for user {user_id}")
        
        return posts
    
    # Test cache-aside pattern
    posts1 = get_user_posts(123)  # From database
    posts2 = get_user_posts(123)  # From cache
    
    # 2. Write-through pattern
    def update_user_profile(user_id, profile_data):
        # Update database (simulated)
        print(f"Updated user {user_id} in database")
        
        # Update cache immediately
        cache_key = f'user_profile_{user_id}'
        cache.set(cache_key, profile_data, timeout=3600)
        print(f"Updated cache for user {user_id}")
    
    # Test write-through pattern
    update_user_profile(123, {'name': 'John Updated', 'email': 'john.updated@example.com'})
    
    # 3. Write-behind pattern (simplified)
    def queue_user_update(user_id, profile_data):
        # Add to update queue in Redis
        queue_key = 'user_update_queue'
        update_data = {
            'user_id': user_id,
            'data': profile_data,
            'timestamp': time.time()
        }
        
        # Use Redis list as queue
        redis_conn = get_redis_connection('default')
        redis_conn.lpush(queue_key, json.dumps(update_data))
        
        # Update cache immediately
        cache_key = f'user_profile_{user_id}'
        cache.set(cache_key, profile_data, timeout=3600)
        print(f"Queued update for user {user_id}")
    
    # Test write-behind pattern
    queue_user_update(456, {'name': 'Jane Doe', 'email': 'jane@example.com'})


def cache_invalidation_strategies():
    """Demonstrate cache invalidation strategies"""
    print("\n=== Cache Invalidation Strategies ===")
    
    # 1. Time-based expiration (TTL)
    cache.set('temp_data', 'This will expire', timeout=5)  # 5 seconds
    print("Set temporary data with 5-second TTL")
    
    time.sleep(2)
    data = cache.get('temp_data')
    print(f"After 2 seconds: {data}")
    
    time.sleep(4)
    data = cache.get('temp_data')
    print(f"After 6 seconds total: {data}")  # Should be None
    
    # 2. Tag-based invalidation
    print("\n2. Tag-based invalidation:")
    
    # Cache data with tags
    redis_cache.set_with_tags('post_1', {'title': 'Post 1'}, tags=['posts', 'user_123'])
    redis_cache.set_with_tags('post_2', {'title': 'Post 2'}, tags=['posts', 'user_123'])
    redis_cache.set_with_tags('comment_1', {'content': 'Comment 1'}, tags=['comments', 'user_123'])
    
    print("Cached posts and comments with tags")
    
    # Invalidate all posts
    redis_cache.invalidate_by_tag('posts')
    print("Invalidated all posts by tag")
    
    # Check what remains
    print(f"Post 1: {cache.get('post_1')}")  # Should be None
    print(f"Comment 1: {cache.get('comment_1')}")  # Should still exist
    
    # 3. Pattern-based invalidation
    print("\n3. Pattern-based invalidation:")
    
    # Set multiple keys with pattern
    cache.set('user_123_profile', {'name': 'User 123'})
    cache.set('user_123_settings', {'theme': 'dark'})
    cache.set('user_456_profile', {'name': 'User 456'})
    
    print("Set user-specific cache keys")
    
    # Invalidate all keys for user 123
    redis_cache.invalidate_pattern('*user_123*')
    print("Invalidated all user_123 keys")
    
    # Check results
    print(f"User 123 profile: {cache.get('user_123_profile')}")  # None
    print(f"User 456 profile: {cache.get('user_456_profile')}")  # Still exists


def session_caching_example():
    """Demonstrate Redis for session storage"""
    print("\n=== Redis Session Storage Example ===")
    
    # Simulate session data
    session_data = {
        'user_id': 123,
        'username': 'johndoe',
        'is_authenticated': True,
        'cart_items': [1, 2, 3],
        'last_activity': time.time()
    }
    
    session_key = 'session_abc123'
    
    # Store session in Redis
    cache.set(session_key, session_data, timeout=1800)  # 30 minutes
    print(f"Stored session: {session_key}")
    
    # Retrieve session
    retrieved_session = cache.get(session_key)
    print(f"Retrieved session: {retrieved_session}")
    
    # Update session
    retrieved_session['last_activity'] = time.time()
    retrieved_session['cart_items'].append(4)
    cache.set(session_key, retrieved_session, timeout=1800)
    print("Updated session data")


def distributed_locking_example():
    """Demonstrate distributed locking with Redis"""
    print("\n=== Distributed Locking Example ===")
    
    redis_conn = get_redis_connection('default')
    
    def acquire_lock(lock_name, timeout=10):
        """Acquire a distributed lock"""
        lock_key = f'lock:{lock_name}'
        identifier = str(time.time())
        
        # Try to acquire lock
        if redis_conn.set(lock_key, identifier, nx=True, ex=timeout):
            return identifier
        return None
    
    def release_lock(lock_name, identifier):
        """Release a distributed lock"""
        lock_key = f'lock:{lock_name}'
        
        # Lua script to ensure atomic release
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        return redis_conn.eval(lua_script, 1, lock_key, identifier)
    
    # Example usage
    lock_name = 'critical_section'
    lock_id = acquire_lock(lock_name)
    
    if lock_id:
        print(f"Acquired lock: {lock_name}")
        
        # Simulate critical section work
        time.sleep(1)
        
        # Release lock
        if release_lock(lock_name, lock_id):
            print(f"Released lock: {lock_name}")
        else:
            print(f"Failed to release lock: {lock_name}")
    else:
        print(f"Failed to acquire lock: {lock_name}")


def cache_warming_example():
    """Demonstrate cache warming strategies"""
    print("\n=== Cache Warming Example ===")
    
    def warm_user_cache(user_id):
        """Pre-populate cache with user data"""
        print(f"Warming cache for user {user_id}")
        
        # Simulate loading data from database
        user_data = {
            'profile': {'id': user_id, 'name': f'User {user_id}'},
            'preferences': {'theme': 'light', 'language': 'en'},
            'recent_posts': [{'id': i, 'title': f'Post {i}'} for i in range(1, 6)]
        }
        
        # Cache different aspects with appropriate TTLs
        cache.set(f'user_profile_{user_id}', user_data['profile'], timeout=3600)
        cache.set(f'user_preferences_{user_id}', user_data['preferences'], timeout=7200)
        cache.set(f'user_recent_posts_{user_id}', user_data['recent_posts'], timeout=1800)
        
        print(f"Warmed cache for user {user_id}")
    
    def warm_popular_content():
        """Pre-populate cache with popular content"""
        print("Warming cache with popular content")
        
        # Simulate popular posts
        popular_posts = [
            {'id': i, 'title': f'Popular Post {i}', 'views': 1000 + i}
            for i in range(1, 11)
        ]
        
        cache.set('popular_posts', popular_posts, timeout=3600)
        
        # Cache individual posts too
        for post in popular_posts:
            cache.set(f'post_{post["id"]}', post, timeout=3600)
        
        print("Warmed popular content cache")
    
    # Warm caches
    warm_user_cache(123)
    warm_popular_content()


def performance_monitoring():
    """Demonstrate Redis performance monitoring"""
    print("\n=== Redis Performance Monitoring ===")
    
    # Get cache statistics
    stats = redis_cache.get_cache_stats()
    print("Redis Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Monitor cache operations
    def monitored_cache_operation():
        start_time = time.time()
        
        # Perform cache operations
        for i in range(100):
            cache.set(f'test_key_{i}', f'test_value_{i}', timeout=60)
        
        for i in range(100):
            cache.get(f'test_key_{i}')
        
        end_time = time.time()
        print(f"100 set + 100 get operations took: {end_time - start_time:.4f} seconds")
        
        # Clean up
        keys_to_delete = [f'test_key_{i}' for i in range(100)]
        cache.delete_many(keys_to_delete)
    
    monitored_cache_operation()


def run_all_redis_examples():
    """Run all Redis caching examples"""
    print("Redis Caching Examples for Django")
    print("=" * 50)
    
    try:
        basic_caching_example()
        advanced_caching_patterns()
        cache_invalidation_strategies()
        session_caching_example()
        distributed_locking_example()
        cache_warming_example()
        performance_monitoring()
        
        print("\n" + "=" * 50)
        print("All Redis examples completed successfully!")
        
    except Exception as e:
        print(f"Error during Redis examples: {e}")
        print("Make sure Redis is running and properly configured")


if __name__ == "__main__":
    # This would be run in Django shell
    print("Run this in Django shell with: python manage.py shell")
    print(">>> from caching_examples.redis_examples import *")
    print(">>> run_all_redis_examples()")