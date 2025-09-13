"""
Repository pattern implementation examples.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Any
from django.db.models import Model, QuerySet
from blog.models import Post, Comment, User


class BaseRepository(ABC):
    """Abstract base repository."""
    
    @abstractmethod
    def get_all(self) -> QuerySet:
        pass
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Model]:
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> Model:
        pass
    
    @abstractmethod
    def update(self, instance: Model, **kwargs) -> Model:
        pass
    
    @abstractmethod
    def delete(self, instance: Model) -> None:
        pass
    
    @abstractmethod
    def filter(self, **kwargs) -> QuerySet:
        pass


class PostRepository(BaseRepository):
    """Repository for Post model operations."""
    
    def __init__(self):
        self.model = Post
    
    def get_all(self):
        return self.model.objects.all()
    
    def get_by_id(self, id: int):
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)
    
    def update(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance):
        instance.delete()
    
    def filter(self, **kwargs):
        return self.model.objects.filter(**kwargs)
    
    # Domain-specific methods
    def get_published_posts(self):
        return self.model.objects.published()
    
    def get_posts_by_author(self, author):
        return self.model.objects.filter(author=author)
    
    def get_recent_posts(self, days=7):
        return self.model.objects.recent(days)
    
    def get_popular_posts(self, min_views=100):
        return self.model.objects.popular(min_views)
    
    def get_trending_posts(self, days=7, limit=10):
        return self.model.objects.trending(days, limit)
    
    def search_posts(self, query):
        return self.model.objects.filter(
            title__icontains=query
        ).union(
            self.model.objects.filter(content__icontains=query)
        )
    
    def get_posts_with_comments(self):
        return self.model.objects.with_comment_count().filter(comment_count__gt=0)


class CommentRepository(BaseRepository):
    """Repository for Comment model operations."""
    
    def __init__(self):
        self.model = Comment
    
    def get_all(self):
        return self.model.objects.all()
    
    def get_by_id(self, id: int):
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)
    
    def update(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance):
        instance.delete()
    
    def filter(self, **kwargs):
        return self.model.objects.filter(**kwargs)
    
    # Domain-specific methods
    def get_comments_for_post(self, post):
        return self.model.objects.filter(post=post, is_approved=True)
    
    def get_comments_by_author(self, author):
        return self.model.objects.filter(author=author)
    
    def get_pending_comments(self):
        return self.model.objects.filter(is_approved=False, is_spam=False)
    
    def get_spam_comments(self):
        return self.model.objects.filter(is_spam=True)
    
    def get_recent_comments(self, days=7):
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.model.objects.filter(created_at__gte=cutoff_date)


class UserRepository(BaseRepository):
    """Repository for User model operations."""
    
    def __init__(self):
        self.model = User
    
    def get_all(self):
        return self.model.objects.all()
    
    def get_by_id(self, id: int):
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def create(self, **kwargs):
        return self.model.objects.create(**kwargs)
    
    def update(self, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance):
        instance.delete()
    
    def filter(self, **kwargs):
        return self.model.objects.filter(**kwargs)
    
    # Domain-specific methods
    def get_by_username(self, username):
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return None
    
    def get_by_email(self, email):
        try:
            return self.model.objects.get(email=email)
        except self.model.DoesNotExist:
            return None
    
    def get_active_users(self):
        return self.model.objects.filter(is_active=True)
    
    def get_staff_users(self):
        return self.model.objects.filter(is_staff=True)
    
    def search_users(self, query):
        return self.model.objects.filter(
            username__icontains=query
        ).union(
            self.model.objects.filter(email__icontains=query)
        ).union(
            self.model.objects.filter(first_name__icontains=query)
        ).union(
            self.model.objects.filter(last_name__icontains=query)
        )


# Repository factory
class RepositoryFactory:
    """Factory for creating repository instances."""
    
    _repositories = {
        'post': PostRepository,
        'comment': CommentRepository,
        'user': UserRepository,
    }
    
    @classmethod
    def get_repository(cls, repository_type: str) -> BaseRepository:
        """Get a repository instance by type."""
        repository_class = cls._repositories.get(repository_type.lower())
        if not repository_class:
            raise ValueError(f"Unknown repository type: {repository_type}")
        return repository_class()
    
    @classmethod
    def register_repository(cls, repository_type: str, repository_class):
        """Register a new repository type."""
        cls._repositories[repository_type.lower()] = repository_class