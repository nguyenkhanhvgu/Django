"""
Signal handlers for the blog application.
"""
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import F
import logging

from ..models import Post, Comment, UserProfile, AuditLog, Notification
from .custom_signals import post_viewed, post_liked, post_shared, comment_added

logger = logging.getLogger(__name__)


# Built-in signal handlers

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created."""
    if created:
        UserProfile.objects.create(user=instance)
        logger.info(f"Created profile for user: {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved."""
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()


@receiver(pre_save, sender=Post)
def log_post_changes(sender, instance, **kwargs):
    """Log changes to post objects."""
    if instance.pk:  # Only for existing posts
        try:
            old_instance = Post.objects.get(pk=instance.pk)
            changes = {}
            
            # Track status changes
            if old_instance.status != instance.status:
                changes['status'] = {
                    'old': old_instance.status,
                    'new': instance.status
                }
            
            # Track title changes
            if old_instance.title != instance.title:
                changes['title'] = {
                    'old': old_instance.title,
                    'new': instance.title
                }
            
            if changes:
                AuditLog.objects.create(
                    user=instance.author,
                    action='update',
                    model_name='Post',
                    object_id=instance.pk,
                    changes=changes
                )
                
        except Post.DoesNotExist:
            pass


@receiver(post_save, sender=Post)
def handle_post_publication(sender, instance, created, **kwargs):
    """Handle post publication events."""
    if created:
        # Log post creation
        AuditLog.objects.create(
            user=instance.author,
            action='create',
            model_name='Post',
            object_id=instance.pk
        )
        logger.info(f"New post created: {instance.title}")
    
    # Handle publication
    if instance.status == 'published' and instance.published_at:
        # Check if this is a new publication
        if created or not Post.objects.filter(
            pk=instance.pk, 
            status='published'
        ).exclude(pk=instance.pk).exists():
            
            # Create notification for followers (simplified)
            # In a real app, you'd have a follower system
            logger.info(f"Post published: {instance.title}")


@receiver(post_delete, sender=Post)
def log_post_deletion(sender, instance, **kwargs):
    """Log when a post is deleted."""
    AuditLog.objects.create(
        user=instance.author,
        action='delete',
        model_name='Post',
        object_id=instance.pk,
        changes={'title': instance.title}
    )
    logger.info(f"Post deleted: {instance.title}")


@receiver(post_save, sender=Comment)
def handle_new_comment(sender, instance, created, **kwargs):
    """Handle new comment creation."""
    if created:
        # Log comment creation
        AuditLog.objects.create(
            user=instance.author,
            action='create',
            model_name='Comment',
            object_id=instance.pk
        )
        
        # Notify post author if it's not their own comment
        if instance.post.author != instance.author:
            Notification.objects.create(
                user=instance.post.author,
                type='comment',
                title='New Comment',
                message=f"{instance.author.username} commented on your post '{instance.post.title}'",
                related_object_id=instance.pk
            )
        
        # Send custom signal
        comment_added.send(
            sender=Comment,
            comment=instance,
            post=instance.post
        )
        
        logger.info(f"New comment by {instance.author.username} on {instance.post.title}")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login events."""
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    AuditLog.objects.create(
        user=user,
        action='login',
        model_name='User',
        object_id=user.pk,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    logger.info(f"User logged in: {user.username} from {ip_address}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout events."""
    if user:
        AuditLog.objects.create(
            user=user,
            action='logout',
            model_name='User',
            object_id=user.pk,
            ip_address=get_client_ip(request)
        )
        logger.info(f"User logged out: {user.username}")


# Custom signal handlers

@receiver(post_viewed)
def track_post_view(sender, post, user, request, **kwargs):
    """Track when a post is viewed."""
    # Update view count atomically
    Post.objects.filter(id=post.id).update(view_count=F('view_count') + 1)
    
    # Log user activity if authenticated
    if user and user.is_authenticated:
        AuditLog.objects.create(
            user=user,
            action='view',
            model_name='Post',
            object_id=post.id,
            ip_address=get_client_ip(request)
        )
    
    logger.debug(f"Post viewed: {post.title}")


@receiver(post_liked)
def handle_post_like(sender, post, user, **kwargs):
    """Handle when a post is liked."""
    # Update like count
    Post.objects.filter(id=post.id).update(like_count=F('like_count') + 1)
    
    # Create notification for post author
    if post.author != user:
        Notification.objects.create(
            user=post.author,
            type='like',
            title='Post Liked',
            message=f"{user.username} liked your post '{post.title}'",
            related_object_id=post.id
        )
    
    # Log the action
    AuditLog.objects.create(
        user=user,
        action='like',
        model_name='Post',
        object_id=post.id
    )
    
    logger.info(f"Post liked: {post.title} by {user.username}")


@receiver(post_shared)
def handle_post_share(sender, post, user, platform, **kwargs):
    """Handle when a post is shared."""
    # Update share count
    Post.objects.filter(id=post.id).update(share_count=F('share_count') + 1)
    
    # Log the share
    AuditLog.objects.create(
        user=user,
        action='share',
        model_name='Post',
        object_id=post.id,
        changes={'platform': platform}
    )
    
    logger.info(f"Post shared: {post.title} on {platform} by {user.username}")


@receiver(comment_added)
def update_post_engagement(sender, comment, post, **kwargs):
    """Update post engagement metrics when a comment is added."""
    # This could trigger additional business logic
    # like updating search indexes, sending notifications, etc.
    logger.debug(f"Comment added to post: {post.title}")


# Utility functions

def get_client_ip(request):
    """Get the client IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Error handling for signals

@receiver(post_save)
def safe_signal_handler(sender, instance, **kwargs):
    """Example of safe signal handling with error catching."""
    try:
        # Your signal logic here
        pass
    except Exception as e:
        logger.error(f"Error in signal handler for {sender.__name__}: {e}", exc_info=True)
        # Don't re-raise to avoid breaking the main flow