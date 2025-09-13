"""
Unit tests for blog models.

These tests focus on testing individual model methods, validation,
and business logic in isolation.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from blog.models import Post, Category, Comment


class PostModelTest(TestCase):
    """Test cases for the Post model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )

    def test_post_creation(self):
        """Test that a post can be created with valid data"""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='This is a test post content.',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.slug, 'test-post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.category, self.category)
        self.assertEqual(post.status, 'published')

    def test_post_str_representation(self):
        """Test the string representation of a post"""
        post = Post.objects.create(
            title='Test Post Title',
            slug='test-post-title',
            content='Test content',
            author=self.user,
            category=self.category
        )
        self.assertEqual(str(post), 'Test Post Title')

    def test_post_get_absolute_url(self):
        """Test the get_absolute_url method"""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            author=self.user,
            category=self.category
        )
        expected_url = f'/blog/{post.slug}/'
        self.assertEqual(post.get_absolute_url(), expected_url)

    def test_post_slug_uniqueness(self):
        """Test that post slugs must be unique"""
        Post.objects.create(
            title='First Post',
            slug='test-slug',
            content='First post content.',
            author=self.user,
            category=self.category
        )
        
        # Creating another post with the same slug should raise ValidationError
        duplicate_post = Post(
            title='Second Post',
            slug='test-slug',
            content='Second post content.',
            author=self.user,
            category=self.category
        )
        
        with self.assertRaises(ValidationError):
            duplicate_post.full_clean()

    def test_post_published_manager(self):
        """Test the published posts manager"""
        # Create published post
        published_post = Post.objects.create(
            title='Published Post',
            slug='published-post',
            content='Published content',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # Create draft post
        Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='Draft content',
            author=self.user,
            category=self.category,
            status='draft'
        )
        
        # Only published posts should be returned
        published_posts = Post.published.all()
        self.assertEqual(published_posts.count(), 1)
        self.assertEqual(published_posts.first(), published_post)

    def test_post_is_published_property(self):
        """Test the is_published property"""
        published_post = Post.objects.create(
            title='Published Post',
            slug='published-post',
            content='Published content',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        draft_post = Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='Draft content',
            author=self.user,
            category=self.category,
            status='draft'
        )
        
        self.assertTrue(published_post.is_published)
        self.assertFalse(draft_post.is_published)

    def test_post_comment_count(self):
        """Test the comment count property"""
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # Initially no comments
        self.assertEqual(post.comment_count, 0)
        
        # Add approved comments
        Comment.objects.create(
            post=post,
            author_name='Commenter 1',
            author_email='commenter1@example.com',
            content='First comment',
            status='approved'
        )
        
        Comment.objects.create(
            post=post,
            author_name='Commenter 2',
            author_email='commenter2@example.com',
            content='Second comment',
            status='approved'
        )
        
        # Add pending comment (should not be counted)
        Comment.objects.create(
            post=post,
            author_name='Commenter 3',
            author_email='commenter3@example.com',
            content='Pending comment',
            status='pending'
        )
        
        # Refresh from database
        post.refresh_from_db()
        self.assertEqual(post.comment_count, 2)


class CategoryModelTest(TestCase):
    """Test cases for the Category model"""

    def test_category_creation(self):
        """Test that a category can be created"""
        category = Category.objects.create(
            name='Technology',
            slug='technology',
            description='Technology related posts'
        )
        
        self.assertEqual(category.name, 'Technology')
        self.assertEqual(category.slug, 'technology')
        self.assertEqual(category.description, 'Technology related posts')

    def test_category_str_representation(self):
        """Test the string representation of a category"""
        category = Category.objects.create(
            name='Technology',
            slug='technology'
        )
        self.assertEqual(str(category), 'Technology')

    def test_category_get_absolute_url(self):
        """Test the get_absolute_url method"""
        category = Category.objects.create(
            name='Technology',
            slug='technology'
        )
        expected_url = f'/blog/category/{category.slug}/'
        self.assertEqual(category.get_absolute_url(), expected_url)

    def test_category_post_count(self):
        """Test the post count property"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        category = Category.objects.create(
            name='Technology',
            slug='technology'
        )
        
        # Initially no posts
        self.assertEqual(category.post_count, 0)
        
        # Add published posts
        Post.objects.create(
            title='Post 1',
            slug='post-1',
            content='Content 1',
            author=user,
            category=category,
            status='published'
        )
        
        Post.objects.create(
            title='Post 2',
            slug='post-2',
            content='Content 2',
            author=user,
            category=category,
            status='published'
        )
        
        # Add draft post (should not be counted)
        Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='Draft content',
            author=user,
            category=category,
            status='draft'
        )
        
        # Refresh from database
        category.refresh_from_db()
        self.assertEqual(category.post_count, 2)


class CommentModelTest(TestCase):
    """Test cases for the Comment model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Technology',
            slug='technology'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            author=self.user,
            category=self.category,
            status='published'
        )

    def test_comment_creation(self):
        """Test that a comment can be created"""
        comment = Comment.objects.create(
            post=self.post,
            author_name='Test Commenter',
            author_email='commenter@example.com',
            content='This is a test comment.',
            status='pending'
        )
        
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author_name, 'Test Commenter')
        self.assertEqual(comment.author_email, 'commenter@example.com')
        self.assertEqual(comment.content, 'This is a test comment.')
        self.assertEqual(comment.status, 'pending')

    def test_comment_str_representation(self):
        """Test the string representation of a comment"""
        comment = Comment.objects.create(
            post=self.post,
            author_name='Test Commenter',
            author_email='commenter@example.com',
            content='This is a test comment.',
        )
        expected_str = f'Comment by Test Commenter on {self.post.title}'
        self.assertEqual(str(comment), expected_str)

    def test_comment_approve_method(self):
        """Test the approve method"""
        comment = Comment.objects.create(
            post=self.post,
            author_name='Test Commenter',
            author_email='commenter@example.com',
            content='This is a test comment.',
            status='pending'
        )
        
        # Initially pending
        self.assertEqual(comment.status, 'pending')
        
        # Approve comment
        comment.approve()
        
        # Should be approved now
        comment.refresh_from_db()
        self.assertEqual(comment.status, 'approved')

    def test_comment_reject_method(self):
        """Test the reject method"""
        comment = Comment.objects.create(
            post=self.post,
            author_name='Test Commenter',
            author_email='commenter@example.com',
            content='This is a test comment.',
            status='pending'
        )
        
        # Initially pending
        self.assertEqual(comment.status, 'pending')
        
        # Reject comment
        comment.reject()
        
        # Should be rejected now
        comment.refresh_from_db()
        self.assertEqual(comment.status, 'rejected')

    def test_comment_is_approved_property(self):
        """Test the is_approved property"""
        approved_comment = Comment.objects.create(
            post=self.post,
            author_name='Approved Commenter',
            author_email='approved@example.com',
            content='Approved comment',
            status='approved'
        )
        
        pending_comment = Comment.objects.create(
            post=self.post,
            author_name='Pending Commenter',
            author_email='pending@example.com',
            content='Pending comment',
            status='pending'
        )
        
        self.assertTrue(approved_comment.is_approved)
        self.assertFalse(pending_comment.is_approved)

    def test_comment_approved_manager(self):
        """Test the approved comments manager"""
        # Create approved comment
        approved_comment = Comment.objects.create(
            post=self.post,
            author_name='Approved Commenter',
            author_email='approved@example.com',
            content='Approved comment',
            status='approved'
        )
        
        # Create pending comment
        Comment.objects.create(
            post=self.post,
            author_name='Pending Commenter',
            author_email='pending@example.com',
            content='Pending comment',
            status='pending'
        )
        
        # Only approved comments should be returned
        approved_comments = Comment.approved.all()
        self.assertEqual(approved_comments.count(), 1)
        self.assertEqual(approved_comments.first(), approved_comment)

    def test_comment_email_validation(self):
        """Test email validation for comments"""
        # Valid email should work
        comment = Comment(
            post=self.post,
            author_name='Test Commenter',
            author_email='valid@example.com',
            content='Test comment'
        )
        comment.full_clean()  # Should not raise ValidationError
        
        # Invalid email should raise ValidationError
        invalid_comment = Comment(
            post=self.post,
            author_name='Test Commenter',
            author_email='invalid-email',
            content='Test comment'
        )
        
        with self.assertRaises(ValidationError):
            invalid_comment.full_clean()

    def test_comment_content_length_validation(self):
        """Test content length validation"""
        # Content too short should raise ValidationError
        short_comment = Comment(
            post=self.post,
            author_name='Test Commenter',
            author_email='test@example.com',
            content='Hi'  # Too short
        )
        
        with self.assertRaises(ValidationError):
            short_comment.full_clean()
        
        # Valid length should work
        valid_comment = Comment(
            post=self.post,
            author_name='Test Commenter',
            author_email='test@example.com',
            content='This is a valid comment with sufficient length.'
        )
        valid_comment.full_clean()  # Should not raise ValidationError