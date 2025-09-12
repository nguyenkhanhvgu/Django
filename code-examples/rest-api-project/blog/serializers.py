"""
Serializers for the blog API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Category, Tag, Comment, Like


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'posts_count']
        read_only_fields = ['date_joined']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'posts_count', 'created_at']
        read_only_fields = ['slug', 'created_at']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'posts_count', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'parent', 'replies', 
            'likes_count', 'is_liked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for Post list view."""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    reading_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'category', 'tags',
            'status', 'featured_image', 'created_at', 'updated_at', 'published_at',
            'views_count', 'comments_count', 'likes_count', 'is_liked', 'reading_time'
        ]

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_reading_time(self, obj):
        # Estimate reading time (average 200 words per minute)
        word_count = len(obj.content.split())
        return max(1, round(word_count / 200))


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for Post detail view."""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    reading_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author', 'category', 'tags',
            'status', 'featured_image', 'created_at', 'updated_at', 'published_at',
            'views_count', 'comments', 'comments_count', 'likes_count', 'is_liked', 'reading_time'
        ]

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_reading_time(self, obj):
        word_count = len(obj.content.split())
        return max(1, round(word_count / 200))


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating posts."""
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'category', 'tags', 
            'status', 'featured_image'
        ]

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return value

    def validate_content(self, value):
        if len(value) < 50:
            raise serializers.ValidationError("Content must be at least 50 characters long.")
        return value

    def validate(self, data):
        if data.get('status') == 'published' and not data.get('content'):
            raise serializers.ValidationError("Published posts must have content.")
        return data


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating comments."""
    
    class Meta:
        model = Comment
        fields = ['content', 'parent']

    def validate_content(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Comment must be at least 3 characters long.")
        return value

    def validate_parent(self, value):
        if value:
            # Ensure parent comment belongs to the same post
            post_id = self.context.get('post_id')
            if value.post.id != post_id:
                raise serializers.ValidationError("Parent comment must belong to the same post.")
        return value


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model."""
    
    class Meta:
        model = Like
        fields = ['id', 'created_at']
        read_only_fields = ['created_at']