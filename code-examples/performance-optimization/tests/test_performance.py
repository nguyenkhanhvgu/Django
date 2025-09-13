"""
Performance tests for Django application.
"""

import time
import statistics
import threading
import queue
from django.test import TestCase, TransactionTestCase, Client
from django.test.utils import override_settings
from django.core.cache import cache
from django.db import connection
from django.contrib.auth.models import User
from blog.models import Author, Post, Category, Tag


class PerformanceTestCase(TestCase):
    """Base class for performance tests."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test data for performance tests."""
        cls.create_test_data()
    
    @classmethod
    def create_test_data(cls):
        """Create comprehensive test data."""
        # Create users and authors
        cls.users = []
        cls.authors = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'author{i}',
                email=f'author{i}@example.com',
                first_name=f'Author',
                last_name=f'{i}'
            )
            author = Author.objects.create(
                user=user,
                bio=f'Bio for author {i}',
                website=f'https://author{i}.example.com'
            )
            cls.users.append(user)
            cls.authors.append(author)
        
        # Create categories
        cls.categories = []
        for i in range(5):
            category = Category.objects.create(
                name=f'Category {i}',
                slug=f'category-{i}',
                description=f'Description for category {i}'
            )
            cls.categories.append(category)
        
        # Create tags
        cls.tags = []
        for i in range(10):
            tag = Tag.objects.create(
                name=f'Tag {i}',
                slug=f'tag-{i}'
            )
            cls.tags.append(tag)
        
        # Create posts
        cls.posts = []
        for i in range(100):
            post = Post.objects.create(
                title=f'Post {i}',
                slug=f'post-{i}',
                author=cls.authors[i % 10],
                content=f'Content for post {i}. ' * 50,  # Longer content
                excerpt=f'Excerpt for post {i}',
                status='published'
            )
            
            # Add categories and tags
            post.categories.set(cls.categories[:2])
            post.tags.set(cls.tags[:3])
            
            cls.posts.append(post)
    
    def setUp(self):
        """Set up for each test."""
        self.client = Client()
        cache.clear()  # Clear cache before each test


class DatabasePerformanceTest(PerformanceTestCase):
    """Test database query performance."""
    
    def test_post_list_query_optimization(self):
        """Test that post list uses optimized queries."""
        with self.assertNumQueries(3):  # Should use select_related and prefetch_related
            response = self.client.get('/posts/')
            self.assertEqual(response.status_code, 200)
    
    def test_post_detail_query_optimization(self):
        """Test that post detail uses optimized queries."""
        post = self.posts[0]
        
        with self.assertNumQueries(4):  # Optimized with select_related and prefetch_related
            response = self.client.get(f'/posts/{post.slug}/')
            self.assertEqual(response.status_code, 200)
    
    def test_category_posts_query_optimization(self):
        """Test that category posts use optimized queries."""
        category = self.categories[0]
        
        with self.assertNumQueries(4):  # Should be optimized
            response = self.client.get(f'/categories/{category.slug}/')
            self.assertEqual(response.status_code, 200)
    
    def test_bulk_operations_performance(self):
        """Test bulk operations performance."""
        start_time = time.time()
        
        # Test bulk create
        new_posts = []
        for i in range(100, 200):
            new_posts.append(Post(
                title=f'Bulk Post {i}',
                slug=f'bulk-post-{i}',
                author=self.authors[i % 10],
                content=f'Bulk content {i}',
                status='published'
            ))
        
        Post.objects.bulk_create(new_posts, batch_size=50)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete quickly
        self.assertLess(execution_time, 1.0)
        self.assertEqual(Post.objects.count(), 200)  # 100 original + 100 new
    
    def test_query_performance_with_large_dataset(self):
        """Test query performance with larger dataset."""
        # Create additional test data
        additional_posts = []
        for i in range(1000):
            additional_posts.append(Post(
                title=f'Large Dataset Post {i}',
                slug=f'large-post-{i}',
                author=self.authors[i % 10],
                content=f'Large dataset content {i}',
                status='published'
            ))
        
        Post.objects.bulk_create(additional_posts, batch_size=100)
        
        # Test query performance
        start_time = time.time()
        posts = list(Post.objects.published().optimized()[:20])
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete quickly even with large dataset
        self.assertLess(execution_time, 0.5)
        self.assertEqual(len(posts), 20)


class CachePerformanceTest(PerformanceTestCase):
    """Test caching performance."""
    
    def test_cache_effectiveness(self):
        """Test that caching improves performance."""
        post = self.posts[0]
        url = f'/posts/{post.slug}/'
        
        # First request - cache miss
        start_time = time.time()
        response1 = self.client.get(url)
        first_request_time = time.time() - start_time
        
        self.assertEqual(response1.status_code, 200)
        
        # Second request - cache hit
        start_time = time.time()
        response2 = self.client.get(url)
        second_request_time = time.time() - start_time
        
        self.assertEqual(response2.status_code, 200)
        
        # Cache hit should be significantly faster
        self.assertLess(second_request_time, first_request_time * 0.8)
    
    def test_cache_invalidation(self):
        """Test cache invalidation works correctly."""
        post = self.posts[0]
        url = f'/posts/{post.slug}/'
        
        # First request to populate cache
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        
        # Modify post to trigger cache invalidation
        post.title = 'Updated Title'
        post.save()
        
        # Request should get updated data
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'Updated Title')
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    def test_performance_without_cache(self):
        """Test performance without caching."""
        post = self.posts[0]
        url = f'/posts/{post.slug}/'
        
        # Multiple requests without cache
        times = []
        for _ in range(5):
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        
        # Without cache, requests should be consistently slower
        self.assertGreater(avg_time, 0.01)  # Adjust threshold as needed


class ConcurrencyPerformanceTest(TransactionTestCase):
    """Test performance under concurrent load."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_test_data()
    
    @classmethod
    def create_test_data(cls):
        """Create test data for concurrency tests."""
        # Create minimal test data
        user = User.objects.create_user(
            username='testauthor',
            email='test@example.com'
        )
        author = Author.objects.create(user=user)
        
        category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        for i in range(20):
            post = Post.objects.create(
                title=f'Concurrent Test Post {i}',
                slug=f'concurrent-post-{i}',
                author=author,
                content=f'Content for concurrent test {i}',
                status='published'
            )
            post.categories.add(category)
    
    def test_concurrent_requests(self):
        """Test performance under concurrent requests."""
        results = queue.Queue()
        
        def make_request():
            client = Client()
            start_time = time.time()
            response = client.get('/posts/')
            end_time = time.time()
            
            results.put({
                'status_code': response.status_code,
                'response_time': end_time - start_time
            })
        
        # Create and start threads
        threads = []
        num_threads = 10
        
        for _ in range(num_threads):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        response_times = []
        while not results.empty():
            result = results.get()
            self.assertEqual(result['status_code'], 200)
            response_times.append(result['response_time'])
        
        # All requests should complete reasonably fast
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        self.assertLess(avg_response_time, 1.0)
        self.assertLess(max_response_time, 2.0)
        self.assertEqual(len(response_times), num_threads)
    
    def test_concurrent_database_operations(self):
        """Test concurrent database operations."""
        results = queue.Queue()
        
        def create_posts():
            try:
                author = Author.objects.first()
                posts = []
                
                for i in range(10):
                    posts.append(Post(
                        title=f'Concurrent DB Post {threading.current_thread().ident}-{i}',
                        slug=f'concurrent-db-{threading.current_thread().ident}-{i}',
                        author=author,
                        content=f'Concurrent content {i}',
                        status='published'
                    ))
                
                Post.objects.bulk_create(posts)
                results.put({'success': True, 'count': len(posts)})
                
            except Exception as e:
                results.put({'success': False, 'error': str(e)})
        
        # Create concurrent database operations
        threads = []
        num_threads = 5
        
        for _ in range(num_threads):
            thread = threading.Thread(target=create_posts)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        successful_operations = 0
        total_created = 0
        
        while not results.empty():
            result = results.get()
            if result['success']:
                successful_operations += 1
                total_created += result['count']
        
        self.assertEqual(successful_operations, num_threads)
        self.assertEqual(total_created, num_threads * 10)


class APIPerformanceTest(PerformanceTestCase):
    """Test API endpoint performance."""
    
    def test_api_posts_list_performance(self):
        """Test API posts list performance."""
        start_time = time.time()
        response = self.client.get('/api/posts/')
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(execution_time, 0.5)
        
        # Check response structure
        data = response.json()
        self.assertIn('posts', data)
        self.assertIsInstance(data['posts'], list)
    
    def test_api_stats_performance(self):
        """Test API stats endpoint performance."""
        start_time = time.time()
        response = self.client.get('/api/stats/')
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(execution_time, 1.0)
        
        # Check response structure
        data = response.json()
        self.assertIn('total_posts', data)
        self.assertIn('total_authors', data)
    
    def test_api_caching_performance(self):
        """Test API endpoint caching."""
        url = '/api/posts/'
        
        # First request
        start_time = time.time()
        response1 = self.client.get(url)
        first_time = time.time() - start_time
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = self.client.get(url)
        second_time = time.time() - start_time
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # Cached request should be faster
        self.assertLess(second_time, first_time * 0.8)


class MemoryPerformanceTest(PerformanceTestCase):
    """Test memory usage performance."""
    
    def test_memory_usage_large_queryset(self):
        """Test memory usage with large querysets."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process large queryset
            posts = Post.objects.all()
            processed_count = 0
            
            for post in posts:
                # Simulate processing
                processed_count += 1
                _ = post.title + post.content
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable
            self.assertLess(memory_increase, 50)  # Less than 50MB increase
            self.assertEqual(processed_count, len(self.posts))
            
        except ImportError:
            self.skipTest("psutil not available for memory testing")
    
    def test_memory_efficient_pagination(self):
        """Test memory-efficient pagination."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024
            
            # Process posts in batches
            from django.core.paginator import Paginator
            
            posts = Post.objects.all()
            paginator = Paginator(posts, 10)
            
            processed_count = 0
            for page_num in paginator.page_range:
                page = paginator.page(page_num)
                for post in page.object_list:
                    processed_count += 1
                    _ = post.title
            
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = final_memory - initial_memory
            
            # Pagination should use less memory
            self.assertLess(memory_increase, 20)  # Less than 20MB increase
            self.assertEqual(processed_count, len(self.posts))
            
        except ImportError:
            self.skipTest("psutil not available for memory testing")