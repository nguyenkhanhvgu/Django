"""
Service layer pattern implementation examples.
"""
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from typing import Optional, List
import logging

from .repositories import PostRepository, CommentRepository, UserRepository
from blog.models import Post, Comment
from blog.signals.custom_signals import post_viewed, post_liked, post_shared, comment_added

logger = logging.getLogger(__name__)


class BaseService:
    """Base service class with common functionality."""
    
    def __init__(self, repository):
        self.repository = repository
    
    def get_all(self):
        return self.repository.get_all()
    
    def get_by_id(self, id):
        return self.repository.get_by_id(id)


class PostService(BaseService):
    """Service layer for Post operations."""
    
    def __init__(self):
        super().__init__(PostRepository())
    
    @transaction.atomic
    def create_post(self, title: str, content: str, author: User, 
                   category=None, tags=None, status='draft') -> Post:
        """Create a new post with validation and business logic."""
        
        # Validation
        self._validate_post_data(title, content, author)
        
        # Create the post
        post_data = {
            'title': title.strip(),
            'content': content.strip(),
            'author': author,
            'status': status,
        }
        
        if category:
            post_data['category'] = category
        
        post = self.repository.create(**post_data)
        
        # Add tags if provided
        if tags:
            post.tags.set(tags)
        
        # Business logic
        self._post_creation_tasks(post)
        
        logger.info(f"Post created: {post.title} by {author.username}")
        return post
    
    def publish_post(self, post_id: int, user: User) -> Post:
        """Publish a post with authorization and business logic."""
        post = self.repository.get_by_id(post_id)
        if not post:
            raise ValidationError("Post not found")
        
        # Authorization check
        if not self._can_publish_post(post, user):
            raise PermissionDenied("You don't have permission to publish this post")
        
        # Business logic validation
        if post.status == 'published':
            raise ValidationError("Post is already published")
        
        # Update post
        post = self.repository.update(
            post, 
            status='published', 
            published_at=timezone.now()
        )
        
        # Post-publication tasks
        self._post_publication_tasks(post)
        
        logger.info(f"Post published: {post.title}")
        return post
    
    def view_post(self, post_id: int, user: User, request) -> Post:
        """Handle post viewing with analytics and business logic."""
        post = self.repository.get_by_id(post_id)
        if not post:
            raise ValidationError("Post not found")
        
        # Check if post is accessible
        if not self._can_view_post(post, user):
            raise PermissionDenied("You don't have permission to view this post")
        
        # Send view signal for analytics
        post_viewed.send(
            sender=Post,
            post=post,
            user=user,
            request=request
        )
        
        return post
    
    def like_post(self, post_id: int, user: User) -> Post:
        """Handle post liking with business logic."""
        post = self.repository.get_by_id(post_id)
        if not post:
            raise ValidationError("Post not found")
        
        # Business logic - users can't like their own posts
        if post.author == user:
            raise ValidationError("You cannot like your own post")
        
        # Send like signal
        post_liked.send(
            sender=Post,
            post=post,
            user=user
        )
        
        return post
    
    def share_post(self, post_id: int, user: User, platform: str) -> Post:
        """Handle post sharing with analytics."""
        post = self.repository.get_by_id(post_id)
        if not post:
            raise ValidationError("Post not found")
        
        # Validate platform
        valid_platforms = ['twitter', 'facebook', 'linkedin', 'email']
        if platform not in valid_platforms:
            raise ValidationError(f"Invalid platform. Must be one of: {valid_platforms}")
        
        # Send share signal
        post_shared.send(
            sender=Post,
            post=post,
            user=user,
            platform=platform
        )
        
        return post
    
    def get_trending_posts(self, days=7, limit=10) -> List[Post]:
        """Get trending posts with business logic."""
        return self.repository.get_trending_posts(days, limit)
    
    def search_posts(self, query: str, user: User) -> List[Post]:
        """Search posts with user-specific filtering."""
        posts = self.repository.search_posts(query)
        
        # Filter based on user permissions
        if not user.is_staff:
            posts = posts.filter(status='published')
        
        return posts
    
    def _validate_post_data(self, title: str, content: str, author: User):
        """Validate post data."""
        if len(title.strip()) < 5:
            raise ValidationError("Title must be at least 5 characters long")
        
        if len(content.strip()) < 50:
            raise ValidationError("Content must be at least 50 characters long")
        
        if not author.is_active:
            raise ValidationError("Author account is not active")
    
    def _can_publish_post(self, post: Post, user: User) -> bool:
        """Check if user can publish the post."""
        return post.author == user or user.is_staff
    
    def _can_view_post(self, post: Post, user: User) -> bool:
        """Check if user can view the post."""
        if post.status == 'published':
            return True
        
        # Draft posts can only be viewed by author or staff
        return post.author == user or user.is_staff
    
    def _post_creation_tasks(self, post: Post):
        """Tasks to perform after post creation."""
        # Could include: indexing for search, cache invalidation, etc.
        pass
    
    def _post_publication_tasks(self, post: Post):
        """Tasks to perform after post publication."""
        # Could include: sending notifications, updating feeds, etc.
        pass


class CommentService(BaseService):
    """Service layer for Comment operations."""
    
    def __init__(self):
        super().__init__(CommentRepository())
    
    @transaction.atomic
    def create_comment(self, post_id: int, content: str, author: User, 
                      parent_id: Optional[int] = None) -> Comment:
        """Create a new comment with validation and business logic."""
        
        # Get the post
        post_repo = PostRepository()
        post = post_repo.get_by_id(post_id)
        if not post:
            raise ValidationError("Post not found")
        
        # Validate comment data
        self._validate_comment_data(content, author, post)
        
        # Handle parent comment for replies
        parent = None
        if parent_id:
            parent = self.repository.get_by_id(parent_id)
            if not parent or parent.post != post:
                raise ValidationError("Invalid parent comment")
        
        # Create comment
        comment = self.repository.create(
            post=post,
            content=content.strip(),
            author=author,
            parent=parent
        )
        
        # Send signal for additional processing
        comment_added.send(
            sender=Comment,
            comment=comment,
            post=post
        )
        
        logger.info(f"Comment created by {author.username} on {post.title}")
        return comment
    
    def moderate_comment(self, comment_id: int, action: str, moderator: User) -> Comment:
        """Moderate a comment (approve, reject, mark as spam)."""
        comment = self.repository.get_by_id(comment_id)
        if not comment:
            raise ValidationError("Comment not found")
        
        # Authorization check
        if not self._can_moderate_comment(comment, moderator):
            raise PermissionDenied("You don't have permission to moderate this comment")
        
        # Apply moderation action
        if action == 'approve':
            comment = self.repository.update(comment, is_approved=True, is_spam=False)
        elif action == 'reject':
            comment = self.repository.update(comment, is_approved=False)
        elif action == 'spam':
            comment = self.repository.update(comment, is_spam=True, is_approved=False)
        else:
            raise ValidationError("Invalid moderation action")
        
        logger.info(f"Comment {action}ed by {moderator.username}")
        return comment
    
    def get_comments_for_post(self, post_id: int, include_replies=True) -> List[Comment]:
        """Get comments for a post with optional reply inclusion."""
        post_repo = PostRepository()
        post = post_repo.get_by_id(post_id)
        if not post:
            raise ValidationError("Post not found")
        
        comments = self.repository.get_comments_for_post(post)
        
        if not include_replies:
            comments = comments.filter(parent__isnull=True)
        
        return comments.order_by('created_at')
    
    def _validate_comment_data(self, content: str, author: User, post: Post):
        """Validate comment data."""
        if len(content.strip()) < 3:
            raise ValidationError("Comment must be at least 3 characters long")
        
        if not author.is_active:
            raise ValidationError("Author account is not active")
        
        # Check if commenting is allowed on this post
        if post.status != 'published':
            raise ValidationError("Cannot comment on unpublished posts")
    
    def _can_moderate_comment(self, comment: Comment, user: User) -> bool:
        """Check if user can moderate the comment."""
        return user.is_staff or comment.post.author == user


class UserService(BaseService):
    """Service layer for User operations."""
    
    def __init__(self):
        super().__init__(UserRepository())
    
    def get_user_stats(self, user_id: int) -> dict:
        """Get comprehensive user statistics."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
        
        post_repo = PostRepository()
        comment_repo = CommentRepository()
        
        # Get user's posts and comments
        user_posts = post_repo.get_posts_by_author(user)
        user_comments = comment_repo.get_comments_by_author(user)
        
        # Calculate statistics
        stats = {
            'total_posts': user_posts.count(),
            'published_posts': user_posts.filter(status='published').count(),
            'total_comments': user_comments.count(),
            'total_views': sum(post.view_count for post in user_posts),
            'total_likes': sum(post.like_count for post in user_posts),
            'avg_engagement': 0,
        }
        
        # Calculate average engagement
        if stats['published_posts'] > 0:
            total_engagement = stats['total_views'] + stats['total_likes']
            stats['avg_engagement'] = total_engagement / stats['published_posts']
        
        return stats
    
    def update_user_profile(self, user_id: int, profile_data: dict, 
                           requesting_user: User) -> User:
        """Update user profile with authorization checks."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValidationError("User not found")
        
        # Authorization check
        if not self._can_update_profile(user, requesting_user):
            raise PermissionDenied("You don't have permission to update this profile")
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email']
        update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
        
        if update_data:
            user = self.repository.update(user, **update_data)
            logger.info(f"Profile updated for user: {user.username}")
        
        return user
    
    def _can_update_profile(self, user: User, requesting_user: User) -> bool:
        """Check if requesting user can update the profile."""
        return user == requesting_user or requesting_user.is_staff


# Service factory
class ServiceFactory:
    """Factory for creating service instances."""
    
    _services = {
        'post': PostService,
        'comment': CommentService,
        'user': UserService,
    }
    
    @classmethod
    def get_service(cls, service_type: str):
        """Get a service instance by type."""
        service_class = cls._services.get(service_type.lower())
        if not service_class:
            raise ValueError(f"Unknown service type: {service_type}")
        return service_class()
    
    @classmethod
    def register_service(cls, service_type: str, service_class):
        """Register a new service type."""
        cls._services[service_type.lower()] = service_class