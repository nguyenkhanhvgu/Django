"""
Cache helper utilities for performance optimization.
"""

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheHelper:
    """Helper class for advanced caching operations."""
    
    @staticmethod
    def get_or_set_complex_data(key, callable_func, timeout=300):
        """
        Get data from cache or execute function and cache result.
        
        Args:
            key (str): Cache key
            callable_func (callable): Function to execute if cache miss
            timeout (int): Cache timeout in seconds
            
        Returns:
            Data from cache or function execution
        """
        data = cache.get(key)
        if data is None:
            try:
                data = callable_func()
                cache.set(key, data, timeout)
                logger.info(f"Cache miss for key: {key}, data cached")
            except Exception as e:
                logger.error(f"Error executing function for cache key {key}: {e}")
                return None
        else:
            logger.debug(f"Cache hit for key: {key}")
        return data
    
    @staticmethod
    def invalidate_related_cache(pattern):
        """
        Invalidate cache keys matching a pattern (Redis only).
        
        Args:
            pattern (str): Pattern to match cache keys
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            keys = redis_conn.keys(f"*{pattern}*")
            if keys:
                redis_conn.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
        except ImportError:
            logger.warning("django_redis not available, cannot invalidate pattern-based cache")
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")
    
    @staticmethod
    def cache_key_from_request(request, prefix="view"):
        """
        Generate cache key from request parameters.
        
        Args:
            request: Django request object
            prefix (str): Key prefix
            
        Returns:
            str: Generated cache key
        """
        key_data = {
            'path': request.path,
            'method': request.method,
            'user_id': request.user.id if request.user.is_authenticated else None,
            'get_params': dict(request.GET),
        }
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    @staticmethod
    def cache_key_with_version(base_key, version_data):
        """
        Generate versioned cache key.
        
        Args:
            base_key (str): Base cache key
            version_data (dict): Data to include in version hash
            
        Returns:
            str: Versioned cache key
        """
        version_string = json.dumps(version_data, sort_keys=True)
        version_hash = hashlib.md5(version_string.encode()).hexdigest()[:8]
        return f"{base_key}:v{version_hash}"
    
    @staticmethod
    def bulk_cache_set(data_dict, timeout=300):
        """
        Set multiple cache keys at once.
        
        Args:
            data_dict (dict): Dictionary of key-value pairs to cache
            timeout (int): Cache timeout in seconds
        """
        try:
            cache.set_many(data_dict, timeout)
            logger.info(f"Bulk cached {len(data_dict)} items")
        except Exception as e:
            logger.error(f"Error in bulk cache set: {e}")
    
    @staticmethod
    def bulk_cache_get(keys):
        """
        Get multiple cache keys at once.
        
        Args:
            keys (list): List of cache keys to retrieve
            
        Returns:
            dict: Dictionary of key-value pairs from cache
        """
        try:
            return cache.get_many(keys)
        except Exception as e:
            logger.error(f"Error in bulk cache get: {e}")
            return {}
    
    @staticmethod
    def cache_with_tags(key, data, tags, timeout=300):
        """
        Cache data with tags for group invalidation (Redis only).
        
        Args:
            key (str): Cache key
            data: Data to cache
            tags (list): List of tags for grouping
            timeout (int): Cache timeout in seconds
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            # Set the main cache entry
            cache.set(key, data, timeout)
            
            # Add key to each tag set
            for tag in tags:
                tag_key = f"tag:{tag}"
                redis_conn.sadd(tag_key, key)
                redis_conn.expire(tag_key, timeout)
                
            logger.info(f"Cached {key} with tags: {tags}")
        except ImportError:
            # Fallback to regular caching without tags
            cache.set(key, data, timeout)
            logger.warning("django_redis not available, caching without tags")
        except Exception as e:
            logger.error(f"Error caching with tags: {e}")
    
    @staticmethod
    def invalidate_by_tags(tags):
        """
        Invalidate all cache entries with specific tags (Redis only).
        
        Args:
            tags (list): List of tags to invalidate
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            
            keys_to_delete = set()
            for tag in tags:
                tag_key = f"tag:{tag}"
                tagged_keys = redis_conn.smembers(tag_key)
                keys_to_delete.update(tagged_keys)
                redis_conn.delete(tag_key)
            
            if keys_to_delete:
                # Convert bytes to strings if needed
                keys_to_delete = [
                    key.decode() if isinstance(key, bytes) else key 
                    for key in keys_to_delete
                ]
                redis_conn.delete(*keys_to_delete)
                logger.info(f"Invalidated {len(keys_to_delete)} cache entries for tags: {tags}")
                
        except ImportError:
            logger.warning("django_redis not available, cannot invalidate by tags")
        except Exception as e:
            logger.error(f"Error invalidating by tags: {e}")


class TemplateFragmentCache:
    """Helper for template fragment caching operations."""
    
    @staticmethod
    def invalidate_fragment(fragment_name, *vary_on):
        """
        Invalidate a template fragment cache.
        
        Args:
            fragment_name (str): Name of the template fragment
            *vary_on: Variables the fragment varies on
        """
        key = make_template_fragment_key(fragment_name, vary_on)
        cache.delete(key)
        logger.info(f"Invalidated template fragment: {fragment_name}")
    
    @staticmethod
    def get_fragment_key(fragment_name, *vary_on):
        """
        Get the cache key for a template fragment.
        
        Args:
            fragment_name (str): Name of the template fragment
            *vary_on: Variables the fragment varies on
            
        Returns:
            str: Template fragment cache key
        """
        return make_template_fragment_key(fragment_name, vary_on)


class CacheStats:
    """Cache statistics and monitoring utilities."""
    
    @staticmethod
    def get_cache_info():
        """
        Get cache information and statistics.
        
        Returns:
            dict: Cache statistics
        """
        try:
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            info = redis_conn.info()
            
            return {
                'backend': 'Redis',
                'used_memory': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses'),
                'hit_rate': (
                    info.get('keyspace_hits', 0) / 
                    max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1)
                ) * 100
            }
        except ImportError:
            return {'backend': 'Default Django Cache', 'info': 'Limited stats available'}
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def monitor_cache_performance(func):
        """
        Decorator to monitor cache performance of a function.
        
        Args:
            func: Function to monitor
            
        Returns:
            Wrapped function with cache monitoring
        """
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            # Get initial cache stats
            try:
                from django_redis import get_redis_connection
                redis_conn = get_redis_connection("default")
                initial_hits = redis_conn.info().get('keyspace_hits', 0)
                initial_misses = redis_conn.info().get('keyspace_misses', 0)
            except:
                initial_hits = initial_misses = 0
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Get final cache stats
            try:
                final_hits = redis_conn.info().get('keyspace_hits', 0)
                final_misses = redis_conn.info().get('keyspace_misses', 0)
                
                hits_during_execution = final_hits - initial_hits
                misses_during_execution = final_misses - initial_misses
                
                execution_time = time.time() - start_time
                
                logger.info(f"Function {func.__name__} executed in {execution_time:.4f}s")
                logger.info(f"Cache hits: {hits_during_execution}, misses: {misses_during_execution}")
                
            except:
                pass
            
            return result
        
        return wrapper