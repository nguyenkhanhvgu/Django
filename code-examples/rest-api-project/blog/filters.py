"""
Custom filters for the blog API.
"""
import django_filters
from django.db.models import Q
from .models import Post, Comment, Category


class PostFilter(django_filters.FilterSet):
    """
    Filter class for Post model with advanced filtering options.
    """
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    author = django_filters.NumberFilter(field_name='author__id')
    author_username = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    category = django_filters.NumberFilter(field_name='category__id')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    tags = django_filters.CharFilter(method='filter_tags')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    
    # Date range filters
    created_date = django_filters.DateFromToRangeFilter(field_name='created_at')
    updated_date = django_filters.DateFromToRangeFilter(field_name='updated_at')
    
    # Boolean filters
    published = django_filters.BooleanFilter()
    featured = django_filters.BooleanFilter()
    
    # Custom filters
    has_comments = django_filters.BooleanFilter(method='filter_has_comments')
    min_comments = django_filters.NumberFilter(method='filter_min_comments')
    
    class Meta:
        model = Post
        fields = {
            'title': ['exact', 'icontains'],
            'published': ['exact'],
            'featured': ['exact'],
            'created_at': ['exact', 'gte', 'lte'],
            'updated_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_tags(self, queryset, name, value):
        """
        Filter posts by tags (comma-separated).
        """
        if not value:
            return queryset
        
        tags = [tag.strip() for tag in value.split(',')]
        query = Q()
        for tag in tags:
            query |= Q(tags__icontains=tag)
        
        return queryset.filter(query)
    
    def filter_has_comments(self, queryset, name, value):
        """
        Filter posts that have or don't have comments.
        """
        if value:
            return queryset.filter(comments__isnull=False).distinct()
        else:
            return queryset.filter(comments__isnull=True)
    
    def filter_min_comments(self, queryset, name, value):
        """
        Filter posts with minimum number of comments.
        """
        from django.db.models import Count
        return queryset.annotate(
            comment_count=Count('comments')
        ).filter(comment_count__gte=value)


class CommentFilter(django_filters.FilterSet):
    """
    Filter class for Comment model.
    """
    post = django_filters.NumberFilter(field_name='post__id')
    post_title = django_filters.CharFilter(field_name='post__title', lookup_expr='icontains')
    author = django_filters.NumberFilter(field_name='author__id')
    author_username = django_filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    created_date = django_filters.DateFromToRangeFilter(field_name='created_at')
    
    # Boolean filters
    approved = django_filters.BooleanFilter()
    is_reply = django_filters.BooleanFilter(method='filter_is_reply')
    
    class Meta:
        model = Comment
        fields = {
            'approved': ['exact'],
            'created_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_is_reply(self, queryset, name, value):
        """
        Filter comments that are replies or top-level comments.
        """
        if value:
            return queryset.filter(parent__isnull=False)
        else:
            return queryset.filter(parent__isnull=True)


class CategoryFilter(django_filters.FilterSet):
    """
    Filter class for Category model.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    has_posts = django_filters.BooleanFilter(method='filter_has_posts')
    min_posts = django_filters.NumberFilter(method='filter_min_posts')
    
    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Category
        fields = {
            'name': ['exact', 'icontains'],
            'created_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_has_posts(self, queryset, name, value):
        """
        Filter categories that have or don't have posts.
        """
        if value:
            return queryset.filter(posts__isnull=False).distinct()
        else:
            return queryset.filter(posts__isnull=True)
    
    def filter_min_posts(self, queryset, name, value):
        """
        Filter categories with minimum number of posts.
        """
        from django.db.models import Count
        return queryset.annotate(
            post_count=Count('posts')
        ).filter(post_count__gte=value)


# Custom filter backends
class CustomSearchFilter(django_filters.rest_framework.DjangoFilterBackend):
    """
    Custom search filter that extends the default DjangoFilterBackend.
    """
    
    def filter_queryset(self, request, queryset, view):
        """
        Apply custom filtering logic.
        """
        queryset = super().filter_queryset(request, queryset, view)
        
        # Add custom search logic here if needed
        search_term = request.query_params.get('q', None)
        if search_term:
            if hasattr(view, 'search_fields'):
                # Implement custom search logic
                search_query = Q()
                for field in view.search_fields:
                    search_query |= Q(**{f"{field}__icontains": search_term})
                queryset = queryset.filter(search_query)
        
        return queryset