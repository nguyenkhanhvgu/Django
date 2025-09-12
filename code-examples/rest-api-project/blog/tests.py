"""
Tests for the blog API.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Post, Category, Tag, Comment, Like


class BlogAPITestCase(APITestCase):
    """Base test case with common setup."""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create tokens
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        
        # Create test category and tag
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
        self.tag = Tag.objects.create(name='Test Tag')
        
        # Create test post
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content with more than fifty characters to pass validation.',
            author=self.user1,
            category=self.category,
            status='published'
        )
        self.post.tags.add(self.tag)


class CategoryAPITest(BlogAPITestCase):
    """Test cases for Category API."""
    
    def test_list_categories(self):
        """Test listing categories."""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Test Category')
    
    def test_create_category_authenticated(self):
        """Test creating category with admin user."""
        self.user1.is_staff = True
        self.user1.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'description': 'New category description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
    
    def test_create_category_unauthorized(self):
        """Test creating category without admin permissions."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        url = reverse('category-list')
        data = {
            'name': 'New Category',
            'description': 'New category description'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PostAPITest(BlogAPITestCase):
    """Test cases for Post API."""
    
    def test_list_posts(self):
        """Test listing posts."""
        url = reverse('post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_post_authenticated(self):
        """Test creating post with authentication."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        url = reverse('post-list')
        data = {
            'title': 'New Test Post',
            'content': 'This is a new test post content with sufficient length to pass validation requirements.',
            'category': self.category.id,
            'status': 'draft'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        
        # Check that author is set correctly
        new_post = Post.objects.get(title='New Test Post')
        self.assertEqual(new_post.author, self.user1)
    
    def test_create_post_unauthenticated(self):
        """Test creating post without authentication."""
        url = reverse('post-list')
        data = {
            'title': 'New Test Post',
            'content': 'This is a new test post content.',
            'category': self.category.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_own_post(self):
        """Test updating own post."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        data = {
            'title': 'Updated Test Post',
            'content': 'This is updated content with sufficient length for validation.',
            'category': self.category.id
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Test Post')
    
    def test_update_other_user_post(self):
        """Test updating another user's post (should fail)."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        data = {
            'title': 'Hacked Post',
            'content': 'This should not work.',
            'category': self.category.id
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_publish_post(self):
        """Test publishing a draft post."""
        # Create a draft post
        draft_post = Post.objects.create(
            title='Draft Post',
            content='This is a draft post content with sufficient length.',
            author=self.user1,
            category=self.category,
            status='draft'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = reverse('post-publish', kwargs={'pk': draft_post.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        draft_post.refresh_from_db()
        self.assertEqual(draft_post.status, 'published')
        self.assertIsNotNone(draft_post.published_at)
    
    def test_like_post(self):
        """Test liking a post."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = reverse('post-like', kwargs={'pk': self.post.pk})
        
        # Like the post
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'liked')
        self.assertEqual(Like.objects.filter(post=self.post, user=self.user1).count(), 1)
        
        # Unlike the post
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'unliked')
        self.assertEqual(Like.objects.filter(post=self.post, user=self.user1).count(), 0)
    
    def test_search_posts(self):
        """Test searching posts."""
        url = reverse('post-list')
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        response = self.client.get(url, {'search': 'Nonexistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_filter_posts_by_category(self):
        """Test filtering posts by category."""
        url = reverse('post-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_my_posts_endpoint(self):
        """Test getting current user's posts."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        url = reverse('post-my-posts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class CommentAPITest(BlogAPITestCase):
    """Test cases for Comment API."""
    
    def test_create_comment(self):
        """Test creating a comment."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        url = reverse('post-comments-list', kwargs={'post_pk': self.post.pk})
        data = {
            'content': 'This is a test comment.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        
        comment = Comment.objects.first()
        self.assertEqual(comment.author, self.user1)
        self.assertEqual(comment.post, self.post)
    
    def test_create_comment_unauthenticated(self):
        """Test creating comment without authentication."""
        url = reverse('post-comments-list', kwargs={'post_pk': self.post.pk})
        data = {
            'content': 'This should not work.'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_comments(self):
        """Test listing comments for a post."""
        # Create a comment
        comment = Comment.objects.create(
            post=self.post,
            author=self.user1,
            content='Test comment'
        )
        
        url = reverse('post-comments-list', kwargs={'post_pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_reply(self):
        """Test creating a reply to a comment."""
        # Create parent comment
        parent_comment = Comment.objects.create(
            post=self.post,
            author=self.user1,
            content='Parent comment'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        url = reverse('post-comments-list', kwargs={'post_pk': self.post.pk})
        data = {
            'content': 'This is a reply.',
            'parent': parent_comment.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        reply = Comment.objects.get(parent=parent_comment)
        self.assertEqual(reply.author, self.user2)
        self.assertEqual(reply.parent, parent_comment)


class AuthenticationTest(APITestCase):
    """Test cases for authentication."""
    
    def test_user_registration(self):
        """Test user registration."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        
        # Check user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
    
    def test_user_login(self):
        """Test user login."""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = reverse('login')
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_logout(self):
        """Test user logout."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        token = Token.objects.create(user=user)
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check token was deleted
        self.assertFalse(Token.objects.filter(user=user).exists())