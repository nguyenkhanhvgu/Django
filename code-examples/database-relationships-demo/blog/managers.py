"""
Custom managers and querysets for the blog app.
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta


class PublishedPostQuerySet(models.QuerySet):
    """Custom QuerySet for published posts with common filters."""
    
    def published(self):
        """Filter for published posts only."""
        return self.filter(status='published')
    
    def by_author(self, author):
        """Filter posts by specific author."""
        return self.filter(author=author)
    
    def by_category(self, category):
        """Filter posts by category."""
        return self.filter(category=category)
    
    def with_tag(self, tag):
        """Filter posts that have a specific tag."""
        return self.filter(tags=tag)
    
    def recent(self, days=7):
        """Filter posts created in the last N days."""
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date)
    
    def popular(self, min_views=100):
        """Filter posts with minimum view count."""
        return self.filter(views__gte=min_views)
    
    def featured(self):
        """Filter featured posts only."""
        return self.filter(featured=True)
    
    def with_comments(self):
        """Filter posts that have approved comments."""
        return self.filter(comments__approved=True).distinct()
    
    def optimized_list(self):
        """Optimized queryset for listing posts with related data."""
        return self.select_related(
            'author', 
            'category', 
            'author__profile'
        ).prefetch_related(
            'tags',
            'comments'
        ).annotate(
            comment_count=models.Count('comments', filter=models.Q(comments__approved=True))
        )


class PublishedPostManager(models.Manager):
    """Custom manager for published posts."""
    
    def get_queryset(self):
        """Return custom queryset."""
        return PublishedPostQuerySet(self.model, using=self._db)
    
    def published(self):
        """Get published posts."""
        return self.get_queryset().published()
    
    def recent_published(self, days=7):
        """Get recently published posts."""
        return self.get_queryset().published().recent(days)
    
    def popular_published(self, min_views=100):
        """Get popular published posts."""
        return self.get_queryset().published().popular(min_views)
    
    def featured_published(self):
        """Get featured published posts."""
        return self.get_queryset().published().featured()
    
    def by_category(self, category):
        """Get published posts by category."""
        return self.get_queryset().published().by_category(category)
    
    def with_tag(self, tag):
        """Get published posts with specific tag."""
        return self.get_queryset().published().with_tag(tag)
    
    def optimized_list(self):
        """Get optimized list of published posts."""
        return self.get_queryset().published().optimized_list()


class CategoryManager(models.Manager):
    """Custom manager for categories."""
    
    def with_post_count(self):
        """Annotate categories with post count."""
        return self.annotate(
            post_count=models.Count('posts', filter=models.Q(posts__status='published'))
        )
    
    def top_level(self):
        """Get top-level categories (no parent)."""
        return self.filter(parent__isnull=True)
    
    def with_children(self):
        """Get categories with their children prefetched."""
        return self.prefetch_related('children')


class TagManager(models.Manager):
    """Custom manager for tags."""
    
    def popular(self, limit=10):
        """Get most popular tags by post count."""
        return self.annotate(
            post_count=models.Count('posts', filter=models.Q(posts__status='published'))
        ).filter(post_count__gt=0).order_by('-post_count')[:limit]
    
    def with_post_count(self):
        """Annotate tags with post count."""
        return self.annotate(
            post_count=models.Count('posts', filter=models.Q(posts__status='published'))
        )