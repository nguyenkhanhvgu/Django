"""
Integration tests for blog workflows.

These tests verify that different components work together correctly,
including services, models, and external integrations.
"""

from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.contrib.auth.models import User
from django.core import mail
from django.test.utils import override_settings
from unittest.mock import patch, Mock

from blog.models import Post, Category, Comment
from blog.services import PostService, NotificationService, CommentModerationService


class PostWorkflowIntegrationTest(TestCase):
    """Test complete post creation and management workflows"""

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

    def test_post_creation_workflow(self):
        """Test the complete post creation workflow"""
        post_data = {
            'title': 'New Blog Post',
            'content': 'This is the content of the new blog post.',
            'category': self.category,
            'author': self.user,
            'tags': ['django', 'testing', 'python']
        }
        
        # Create post using service
        post = PostService.create_post(**post_data)
        
        # Verify post was created correctly
        self.assertTrue(Post.objects.filter(title='New Blog Post').exists())
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.category, self.category)
        self.assertEqual(post.status, 'draft')  # Default status
        
        # Verify slug was generated
        self.assertEqual(post.slug, 'new-blog-post')
        
        # Verify tags were created and associated
        self.assertEqual(post.tags.count(), 3)
        tag_names = [tag.name for tag in post.tags.all()]
        self.assertIn('django', tag_names)
        self.assertIn('testing', tag_names)
        self.assertIn('python', tag_names)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_post_publication_with_notifications(self):
        """Test post publication triggers notifications"""
        # Create draft post
        post = Post.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='This is a draft post.',
            author=self.user,
            category=self.category,
            status='draft'
        )
        
        # Create subscribers
        subscriber1 = User.objects.create_user(
            username='subscriber1',
            email='subscriber1@example.com'
        )
        subscriber2 = User.objects.create_user(
            username='subscriber2',
            email='subscriber2@example.com'
        )
        
        # Subscribe users to category
        self.category.subscribers.add(subscriber1, subscriber2)
        
        # Publish post using service
        PostService.publish_post(post)
        
        # Verify post is published
        post.refresh_from_db()
        self.assertEqual(post.status, 'published')
        self.assertIsNotNone(post.published_at)
        
        # Verify notifications were sent
        self.assertEqual(len(mail.outbox), 2)  # One for each subscriber
        
        # Verify email content
        email_subjects = [email.subject for email in mail.outbox]
        self.assertIn('New Post: Draft Post', email_subjects[0])
        
        # Verify recipients
        recipients = []
        for email in mail.outbox:
            recipients.extend(email.to)
        self.assertIn('subscriber1@example.com', recipients)
        self.assertIn('subscriber2@example.com', recipients)

    def test_post_update_workflow(self):
        """Test post update workflow with version tracking"""
        # Create initial post
        post = Post.objects.create(
            title='Original Title',
            slug='original-title',
            content='Original content',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # Update post using service
        update_data = {
            'title': 'Updated Title',
            'content': 'Updated content with more information.',
            'category': self.category
        }
        
        updated_post = PostService.update_post(post, **update_data)
        
        # Verify post was updated
        self.assertEqual(updated_post.title, 'Updated Title')
        self.assertEqual(updated_post.content, 'Updated content with more information.')
        
        # Verify version was created
        self.assertTrue(updated_post.versions.exists())
        latest_version = updated_post.versions.latest('created_at')
        self.assertEqual(latest_version.title, 'Original Title')
        self.assertEqual(latest_version.content, 'Original content')

    def test_post_deletion_workflow(self):
        """Test post deletion workflow with cleanup"""
        # Create post with comments and tags
        post = Post.objects.create(
            title='Post to Delete',
            slug='post-to-delete',
            content='This post will be deleted.',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # Add comments
        comment1 = Comment.objects.create(
            post=post,
            author_name='Commenter 1',
            author_email='commenter1@example.com',
            content='First comment',
            status='approved'
        )
        
        comment2 = Comment.objects.create(
            post=post,
            author_name='Commenter 2',
            author_email='commenter2@example.com',
            content='Second comment',
            status='approved'
        )
        
        # Add tags
        post.tags.create(name='tag1')
        post.tags.create(name='tag2')
        
        post_id = post.id
        comment_ids = [comment1.id, comment2.id]
        
        # Delete post using service
        PostService.delete_post(post)
        
        # Verify post is deleted
        self.assertFalse(Post.objects.filter(id=post_id).exists())
        
        # Verify comments are deleted (cascade)
        for comment_id in comment_ids:
            self.assertFalse(Comment.objects.filter(id=comment_id).exists())
        
        # Verify orphaned tags are cleaned up
        self.assertFalse(post.tags.exists())


class CommentModerationWorkflowTest(TestCase):
    """Test comment moderation workflows"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='modpass123',
            is_staff=True
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

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_comment_submission_and_moderation_workflow(self):
        """Test complete comment submission and moderation workflow"""
        # Submit comment
        comment_data = {
            'post': self.post,
            'author_name': 'Test Commenter',
            'author_email': 'commenter@example.com',
            'content': 'This is a test comment that needs moderation.',
            'ip_address': '192.168.1.1'
        }
        
        comment = CommentModerationService.submit_comment(**comment_data)
        
        # Verify comment is created with pending status
        self.assertEqual(comment.status, 'pending')
        self.assertEqual(comment.post, self.post)
        
        # Verify moderation notification was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('New Comment for Moderation', mail.outbox[0].subject)
        self.assertIn('moderator@example.com', mail.outbox[0].to)
        
        # Clear mail outbox
        mail.outbox = []
        
        # Moderate comment (approve)
        CommentModerationService.approve_comment(comment, self.moderator)
        
        # Verify comment is approved
        comment.refresh_from_db()
        self.assertEqual(comment.status, 'approved')
        self.assertEqual(comment.moderated_by, self.moderator)
        self.assertIsNotNone(comment.moderated_at)
        
        # Verify approval notification was sent to commenter
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Comment Approved', mail.outbox[0].subject)
        self.assertIn('commenter@example.com', mail.outbox[0].to)

    def test_spam_detection_workflow(self):
        """Test automatic spam detection workflow"""
        # Submit comment with spam indicators
        spam_comment_data = {
            'post': self.post,
            'author_name': 'Spammer',
            'author_email': 'spam@spam.com',
            'content': 'Buy cheap products now! Visit http://spam-site.com for amazing deals!',
            'ip_address': '192.168.1.100'
        }
        
        comment = CommentModerationService.submit_comment(**spam_comment_data)
        
        # Verify comment is automatically marked as spam
        self.assertEqual(comment.status, 'spam')
        self.assertTrue(comment.is_spam)
        
        # Verify spam score is calculated
        self.assertGreater(comment.spam_score, 0.5)

    def test_bulk_comment_moderation(self):
        """Test bulk comment moderation workflow"""
        # Create multiple pending comments
        comments = []
        for i in range(5):
            comment = Comment.objects.create(
                post=self.post,
                author_name=f'Commenter {i}',
                author_email=f'commenter{i}@example.com',
                content=f'This is comment number {i}',
                status='pending'
            )
            comments.append(comment)
        
        comment_ids = [comment.id for comment in comments]
        
        # Bulk approve comments
        CommentModerationService.bulk_approve_comments(comment_ids, self.moderator)
        
        # Verify all comments are approved
        approved_comments = Comment.objects.filter(id__in=comment_ids, status='approved')
        self.assertEqual(approved_comments.count(), 5)
        
        # Verify all have moderation info
        for comment in approved_comments:
            self.assertEqual(comment.moderated_by, self.moderator)
            self.assertIsNotNone(comment.moderated_at)


class NotificationIntegrationTest(TestCase):
    """Test notification system integration"""

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

    @patch('blog.services.NotificationService.send_email')
    def test_notification_service_integration(self, mock_send_email):
        """Test notification service integration with external email service"""
        mock_send_email.return_value = True
        
        # Create post
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # Send notification
        NotificationService.notify_new_post(post)
        
        # Verify external email service was called
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        self.assertIn('New Post: Test Post', call_args[1]['subject'])

    @patch('requests.post')
    def test_webhook_notification_integration(self, mock_post):
        """Test webhook notification integration"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success'}
        mock_post.return_value = mock_response
        
        # Create post
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        # Send webhook notification
        NotificationService.send_webhook_notification(post)
        
        # Verify webhook was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn('webhook', call_args[0][0])  # URL contains 'webhook'
        
        # Verify payload
        payload = call_args[1]['json']
        self.assertEqual(payload['event'], 'post_published')
        self.assertEqual(payload['post']['title'], 'Test Post')


class DatabaseTransactionIntegrationTest(TransactionTestCase):
    """Test database transaction handling in workflows"""

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

    def test_post_creation_transaction_rollback(self):
        """Test that post creation rolls back on error"""
        initial_post_count = Post.objects.count()
        
        # Attempt to create post with error in transaction
        with self.assertRaises(Exception):
            with transaction.atomic():
                post = Post.objects.create(
                    title='Test Post',
                    slug='test-post',
                    content='Test content',
                    author=self.user,
                    category=self.category
                )
                
                # Create related objects
                Comment.objects.create(
                    post=post,
                    author_name='Commenter',
                    author_email='commenter@example.com',
                    content='Test comment'
                )
                
                # Force an error to trigger rollback
                raise Exception('Forced error for testing')
        
        # Verify nothing was created due to rollback
        self.assertEqual(Post.objects.count(), initial_post_count)
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_moderation_atomic_operation(self):
        """Test that comment moderation is atomic"""
        # Create post and comment
        post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            content='Test content',
            author=self.user,
            category=self.category,
            status='published'
        )
        
        comment = Comment.objects.create(
            post=post,
            author_name='Commenter',
            author_email='commenter@example.com',
            content='Test comment',
            status='pending'
        )
        
        # Mock a service that might fail
        with patch('blog.services.NotificationService.send_approval_notification') as mock_notify:
            mock_notify.side_effect = Exception('Email service down')
            
            # Attempt to approve comment
            with self.assertRaises(Exception):
                with transaction.atomic():
                    comment.status = 'approved'
                    comment.save()
                    
                    # This should fail and rollback the status change
                    NotificationService.send_approval_notification(comment)
        
        # Verify comment status was rolled back
        comment.refresh_from_db()
        self.assertEqual(comment.status, 'pending')

    def test_bulk_operations_transaction_handling(self):
        """Test transaction handling in bulk operations"""
        # Create multiple posts
        posts_data = [
            {
                'title': f'Post {i}',
                'slug': f'post-{i}',
                'content': f'Content {i}',
                'author': self.user,
                'category': self.category
            }
            for i in range(5)
        ]
        
        initial_count = Post.objects.count()
        
        # Bulk create with potential error
        try:
            with transaction.atomic():
                for i, post_data in enumerate(posts_data):
                    Post.objects.create(**post_data)
                    
                    # Simulate error on 3rd post
                    if i == 2:
                        raise Exception('Simulated error')
        except Exception:
            pass
        
        # Verify no posts were created due to rollback
        self.assertEqual(Post.objects.count(), initial_count)
        
        # Now create successfully
        with transaction.atomic():
            for post_data in posts_data:
                Post.objects.create(**post_data)
        
        # Verify all posts were created
        self.assertEqual(Post.objects.count(), initial_count + 5)