from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Post, Comment


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            body='This is a test post.',
            status='published'
        )

    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.slug, 'test-post')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.status, 'published')

    def test_post_str_representation(self):
        self.assertEqual(str(self.post), 'Test Post')

    def test_post_absolute_url(self):
        url = self.post.get_absolute_url()
        expected_url = reverse('blog:post_detail', args=[
            self.post.publish.year,
            self.post.publish.month,
            self.post.publish.day,
            self.post.slug
        ])
        self.assertEqual(url, expected_url)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            author=self.user,
            body='This is a test post.',
            status='published'
        )
        self.comment = Comment.objects.create(
            post=self.post,
            name='Test Commenter',
            email='commenter@example.com',
            body='This is a test comment.'
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.name, 'Test Commenter')
        self.assertEqual(self.comment.email, 'commenter@example.com')
        self.assertEqual(self.comment.body, 'This is a test comment.')
        self.assertTrue(self.comment.active)

    def test_comment_str_representation(self):
        expected_str = f'Comment by {self.comment.name} on {self.post}'
        self.assertEqual(str(self.comment), expected_str)