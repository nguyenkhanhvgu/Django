# Database Sharding Implementation Examples

import hashlib
from typing import Dict, List, Any, Optional
from django.db import models, connections
from django.conf import settings

# Database router for sharding
class ShardRouter:
    """
    Database router that implements horizontal sharding based on user ID
    """
    
    def __init__(self):
        self.shard_map = {
            'shard1': ['user_1', 'user_2', 'user_3'],
            'shard2': ['user_4', 'user_5', 'user_6'],
            'shard3': ['user_7', 'user_8', 'user_9'],
        }
    
    def db_for_read(self, model, **hints):
        """Route read operations to appropriate shard"""
        if model._meta.app_label == 'users':
            instance = hints.get('instance')
            if instance and hasattr(instance, 'user_id'):
                return self._get_shard_for_user(instance.user_id)
        return None
    
    def db_for_write(self, model, **hints):
        """Route write operations to appropriate shard"""
        if model._meta.app_label == 'users':
            instance = hints.get('instance')
            if instance and hasattr(instance, 'user_id'):
                return self._get_shard_for_user(instance.user_id)
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if objects are on the same shard"""
        db_set = {'shard1', 'shard2', 'shard3'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return obj1._state.db == obj2._state.db
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Control which apps/models can be migrated to which databases"""
        if app_label == 'users':
            return db in ['shard1', 'shard2', 'shard3']
        elif db in ['shard1', 'shard2', 'shard3']:
            return False
        return None
    
    def _get_shard_for_user(self, user_id: int) -> str:
        """Determine which shard a user belongs to"""
        # Simple modulo-based sharding
        shard_count = 3
        shard_index = user_id % shard_count
        return f'shard{shard_index + 1}'

# Hash-based sharding router
class HashShardRouter:
    """
    More sophisticated sharding using consistent hashing
    """
    
    def __init__(self):
        self.shards = ['shard1', 'shard2', 'shard3', 'shard4']
        self.virtual_nodes = 150  # Virtual nodes per physical shard
        self.ring = {}
        self._build_ring()
    
    def _build_ring(self):
        """Build consistent hash ring"""
        for shard in self.shards:
            for i in range(self.virtual_nodes):
                key = f"{shard}:{i}"
                hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
                self.ring[hash_value] = shard
    
    def _get_shard_for_key(self, key: str) -> str:
        """Get shard for a given key using consistent hashing"""
        if not self.ring:
            return self.shards[0]
        
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        
        # Find the first node in the ring >= hash_value
        for ring_key in sorted(self.ring.keys()):
            if ring_key >= hash_value:
                return self.ring[ring_key]
        
        # Wrap around to the first node
        return self.ring[min(self.ring.keys())]
    
    def db_for_read(self, model, **hints):
        """Route reads using consistent hashing"""
        if model._meta.app_label == 'users':
            instance = hints.get('instance')
            if instance and hasattr(instance, 'user_id'):
                key = f"user:{instance.user_id}"
                return self._get_shard_for_key(key)
        return None
    
    def db_for_write(self, model, **hints):
        """Route writes using consistent hashing"""
        if model._meta.app_label == 'users':
            instance = hints.get('instance')
            if instance and hasattr(instance, 'user_id'):
                key = f"user:{instance.user_id}"
                return self._get_shard_for_key(key)
        return None

# Shard-aware model manager
class ShardedManager(models.Manager):
    """
    Custom manager that handles cross-shard queries
    """
    
    def get_from_all_shards(self, **kwargs):
        """Query across all shards and combine results"""
        results = []
        shard_databases = ['shard1', 'shard2', 'shard3']
        
        for db in shard_databases:
            try:
                queryset = self.using(db).filter(**kwargs)
                results.extend(list(queryset))
            except Exception as e:
                # Log error but continue with other shards
                print(f"Error querying shard {db}: {e}")
        
        return results
    
    def get_by_shard_key(self, shard_key: Any, **kwargs):
        """Get objects from specific shard based on shard key"""
        router = HashShardRouter()
        shard = router._get_shard_for_key(str(shard_key))
        return self.using(shard).filter(**kwargs)

# Shard-aware model base class
class ShardedModel(models.Model):
    """
    Base model class for sharded models
    """
    
    objects = ShardedManager()
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Override save to ensure correct shard routing"""
        if hasattr(self, 'get_shard_key'):
            router = HashShardRouter()
            shard = router._get_shard_for_key(str(self.get_shard_key()))
            kwargs['using'] = shard
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to ensure correct shard routing"""
        if hasattr(self, 'get_shard_key'):
            router = HashShardRouter()
            shard = router._get_shard_for_key(str(self.get_shard_key()))
            kwargs['using'] = shard
        super().delete(*args, **kwargs)

# Example sharded models
class User(ShardedModel):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_shard_key(self):
        return f"user:{self.id}"

class UserProfile(ShardedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    
    def get_shard_key(self):
        return f"user:{self.user_id}"

class Post(ShardedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_shard_key(self):
        return f"user:{self.user_id}"

# Cross-shard aggregation service
class CrossShardAggregator:
    """
    Service for performing aggregations across multiple shards
    """
    
    def __init__(self):
        self.shard_databases = ['shard1', 'shard2', 'shard3']
    
    def count_total_users(self) -> int:
        """Count total users across all shards"""
        total = 0
        for db in self.shard_databases:
            try:
                count = User.objects.using(db).count()
                total += count
            except Exception as e:
                print(f"Error counting users in shard {db}: {e}")
        return total
    
    def get_recent_posts(self, limit: int = 100) -> List[Post]:
        """Get recent posts from all shards"""
        all_posts = []
        
        for db in self.shard_databases:
            try:
                posts = Post.objects.using(db).order_by('-created_at')[:limit]
                all_posts.extend(list(posts))
            except Exception as e:
                print(f"Error fetching posts from shard {db}: {e}")
        
        # Sort combined results and return top N
        all_posts.sort(key=lambda p: p.created_at, reverse=True)
        return all_posts[:limit]
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get aggregated user statistics"""
        stats = {
            'total_users': 0,
            'users_per_shard': {},
            'recent_signups': 0
        }
        
        from datetime import datetime, timedelta
        recent_date = datetime.now() - timedelta(days=7)
        
        for db in self.shard_databases:
            try:
                total_in_shard = User.objects.using(db).count()
                recent_in_shard = User.objects.using(db).filter(
                    created_at__gte=recent_date
                ).count()
                
                stats['total_users'] += total_in_shard
                stats['users_per_shard'][db] = total_in_shard
                stats['recent_signups'] += recent_in_shard
                
            except Exception as e:
                print(f"Error getting stats from shard {db}: {e}")
        
        return stats

# Shard management utilities
class ShardManager:
    """
    Utilities for managing shards
    """
    
    def __init__(self):
        self.shard_databases = ['shard1', 'shard2', 'shard3']
    
    def migrate_user_to_shard(self, user_id: int, target_shard: str):
        """Migrate a user and their data to a different shard"""
        # This is a complex operation that would need careful implementation
        # in a real system with proper transaction handling and data consistency
        
        source_shard = self._find_user_shard(user_id)
        if source_shard == target_shard:
            return  # Already on target shard
        
        # Begin migration process
        try:
            # 1. Copy user data to target shard
            user = User.objects.using(source_shard).get(id=user_id)
            user.save(using=target_shard)
            
            # 2. Copy related data
            profile = UserProfile.objects.using(source_shard).filter(user_id=user_id)
            for p in profile:
                p.save(using=target_shard)
            
            posts = Post.objects.using(source_shard).filter(user_id=user_id)
            for post in posts:
                post.save(using=target_shard)
            
            # 3. Delete from source shard (after verification)
            # This would need additional safety checks in production
            
        except Exception as e:
            print(f"Error migrating user {user_id}: {e}")
            # Rollback logic would go here
    
    def _find_user_shard(self, user_id: int) -> Optional[str]:
        """Find which shard contains a specific user"""
        for db in self.shard_databases:
            try:
                if User.objects.using(db).filter(id=user_id).exists():
                    return db
            except Exception:
                continue
        return None
    
    def rebalance_shards(self):
        """Rebalance data across shards (simplified implementation)"""
        # This would be a complex operation in production
        # involving careful planning and minimal downtime
        
        stats = CrossShardAggregator().get_user_statistics()
        print("Current shard distribution:", stats['users_per_shard'])
        
        # Identify imbalanced shards and plan migrations
        # Implementation would depend on specific rebalancing strategy

# Database settings for sharding
SHARDED_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'main_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'shard1': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shard1_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'shard1.example.com',
        'PORT': '5432',
    },
    'shard2': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shard2_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'shard2.example.com',
        'PORT': '5432',
    },
    'shard3': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shard3_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'shard3.example.com',
        'PORT': '5432',
    },
}

# Usage examples
if __name__ == "__main__":
    # Example usage of sharded models
    
    # Create users (will be automatically sharded)
    user1 = User.objects.create(username='user1', email='user1@example.com')
    user2 = User.objects.create(username='user2', email='user2@example.com')
    
    # Query from specific shard
    shard1_users = User.objects.using('shard1').all()
    
    # Cross-shard queries
    all_users = User.objects.get_from_all_shards()
    
    # Aggregations
    aggregator = CrossShardAggregator()
    total_users = aggregator.count_total_users()
    user_stats = aggregator.get_user_statistics()
    
    print(f"Total users across all shards: {total_users}")
    print(f"User statistics: {user_stats}")