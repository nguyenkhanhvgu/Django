"""
Factory Boy factories for generating test data.

These factories provide a convenient way to create test objects
with realistic data for testing purposes.
"""

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from blog.models import Post, Category, Comment, Tag


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances"""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False
    date_joined = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password for the user"""
        if not create:
            return
        
        password = extracted or 'defaultpass123'
        self.set_password(password)
        self.save()


class StaffUserFactory(UserFactory):
    """Factory for creating staff User instances"""
    
    is_staff = True


class SuperUserFactory(UserFactory):
    """Factory for creating superuser User instances"""
    
    is_staff = True
    is_superuser = True


class CategoryFactory(DjangoModelFactory):
    """Factory for creating Category instances"""
    
    class Meta:
        model = Category
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    description = factory.Faker('text', max_nb_chars=200)
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def subscribers(self, create, extracted, **kwargs):
        """Add subscribers to the category"""
        if not create:
            return
        
        if extracted:
            for user in extracted:
                self.subscribers.add(user)


class TagFactory(DjangoModelFactory):
    """Factory for creating Tag instances"""
    
    class Meta:
        model = Tag
    
    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))


class PostFactory(DjangoModelFactory):
    """Factory for creating Post instances"""
    
    class Meta:
        model = Post
    
    title = factory.Faker('sentence', nb_words=4)
    slug = factory.LazyAttribute(lambda obj: obj.title.lower().replace(' ', '-').replace('.', ''))
    content = factory.Faker('text', max_nb_chars=1000)
    excerpt = factory.LazyAttribute(lambda obj: obj.content[:150] + '...' if len(obj.content) > 150 else obj.content)
    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    status = 'published'
    featured = False
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
    published_at = factory.LazyAttribute(lambda obj: obj.created_at if obj.status == 'published' else None)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Add tags to the post"""
        if not create:
            return
        
        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        else:
            # Create 2-4 random tags by default
            tag_count = factory.Faker('random_int', min=2, max=4).generate()
            for _ in range(tag_count):
                tag = TagFactory()
                self.tags.add(tag)


class DraftPostFactory(PostFactory):
    """Factory for creating draft Post instances"""
    
    status = 'draft'
    published_at = None


class FeaturedPostFactory(PostFactory):
    """Factory for creating featured Post instances"""
    
    featured = True
    status = 'published'


class OldPostFactory(PostFactory):
    """Factory for creating old Post instances"""
    
    created_at = factory.LazyFunction(lambda: timezone.now() - timedelta(days=365))
    updated_at = factory.LazyAttribute(lambda obj: obj.created_at)
    published_at = factory.LazyAttribute(lambda obj: obj.created_at)


class CommentFactory(DjangoModelFactory):
    """Factory for creating Comment instances"""
    
    class Meta:
        model = Comment
    
    post = factory.SubFactory(PostFactory)
    author_name = factory.Faker('name')
    author_email = factory.Faker('email')
    author_url = factory.Faker('url')
    content = factory.Faker('text', max_nb_chars=500)
    ip_address = factory.Faker('ipv4')
    user_agent = factory.Faker('user_agent')
    status = 'approved'
    is_spam = False
    spam_score = 0.0
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class PendingCommentFactory(CommentFactory):
    """Factory for creating pending Comment instances"""
    
    status = 'pending'


class SpamCommentFactory(CommentFactory):
    """Factory for creating spam Comment instances"""
    
    status = 'spam'
    is_spam = True
    spam_score = factory.Faker('pyfloat', left_digits=0, right_digits=2, positive=True, min_value=0.5, max_value=1.0)
    content = factory.LazyFunction(
        lambda: 'Buy cheap products now! Visit http://spam-site.com for amazing deals! ' + 
                factory.Faker('text', max_nb_chars=200).generate()
    )


class RejectedCommentFactory(CommentFactory):
    """Factory for creating rejected Comment instances"""
    
    status = 'rejected'
    moderated_by = factory.SubFactory(StaffUserFactory)
    moderated_at = factory.LazyFunction(timezone.now)


class ApprovedCommentFactory(CommentFactory):
    """Factory for creating approved Comment instances"""
    
    status = 'approved'
    moderated_by = factory.SubFactory(StaffUserFactory)
    moderated_at = factory.LazyFunction(timezone.now)


# Trait factories for common combinations
class PostWithCommentsFactory(PostFactory):
    """Factory for creating Post instances with comments"""
    
    @factory.post_generation
    def comments(self, create, extracted, **kwargs):
        """Add comments to the post"""
        if not create:
            return
        
        if extracted:
            comment_count = extracted
        else:
            comment_count = factory.Faker('random_int', min=1, max=5).generate()
        
        for _ in range(comment_count):
            CommentFactory(post=self)


class CategoryWithPostsFactory(CategoryFactory):
    """Factory for creating Category instances with posts"""
    
    @factory.post_generation
    def posts(self, create, extracted, **kwargs):
        """Add posts to the category"""
        if not create:
            return
        
        if extracted:
            post_count = extracted
        else:
            post_count = factory.Faker('random_int', min=3, max=10).generate()
        
        for _ in range(post_count):
            PostFactory(category=self)


class UserWithPostsFactory(UserFactory):
    """Factory for creating User instances with posts"""
    
    @factory.post_generation
    def posts(self, create, extracted, **kwargs):
        """Add posts to the user"""
        if not create:
            return
        
        if extracted:
            post_count = extracted
        else:
            post_count = factory.Faker('random_int', min=2, max=8).generate()
        
        for _ in range(post_count):
            PostFactory(author=self)


# Batch factories for creating multiple related objects
def create_blog_data(
    users=5,
    categories=3,
    posts_per_category=10,
    comments_per_post=3,
    tags=20
):
    """
    Create a complete blog dataset for testing.
    
    Args:
        users: Number of users to create
        categories: Number of categories to create
        posts_per_category: Number of posts per category
        comments_per_post: Average number of comments per post
        tags: Number of tags to create
    
    Returns:
        dict: Dictionary containing created objects
    """
    # Create users
    regular_users = UserFactory.create_batch(users - 2)
    staff_user = StaffUserFactory()
    super_user = SuperUserFactory()
    all_users = regular_users + [staff_user, super_user]
    
    # Create tags
    all_tags = TagFactory.create_batch(tags)
    
    # Create categories with posts
    all_categories = []
    all_posts = []
    all_comments = []
    
    for _ in range(categories):
        category = CategoryFactory()
        all_categories.append(category)
        
        # Create posts for this category
        for _ in range(posts_per_category):
            # Randomly assign author
            author = factory.Faker('random_element', elements=all_users).generate()
            
            # Randomly assign status (80% published, 20% draft)
            status = factory.Faker('random_element', elements=('published', 'published', 'published', 'published', 'draft')).generate()
            
            post = PostFactory(
                author=author,
                category=category,
                status=status
            )
            
            # Add random tags (2-5 tags per post)
            post_tags = factory.Faker('random_elements', elements=all_tags, length=factory.Faker('random_int', min=2, max=5).generate(), unique=True).generate()
            post.tags.set(post_tags)
            
            all_posts.append(post)
            
            # Create comments for published posts
            if status == 'published':
                comment_count = factory.Faker('random_int', min=0, max=comments_per_post * 2).generate()
                
                for _ in range(comment_count):
                    # 70% approved, 20% pending, 10% spam
                    comment_status = factory.Faker('random_element', elements=('approved', 'approved', 'approved', 'approved', 'approved', 'approved', 'approved', 'pending', 'pending', 'spam')).generate()
                    
                    if comment_status == 'spam':
                        comment = SpamCommentFactory(post=post)
                    elif comment_status == 'pending':
                        comment = PendingCommentFactory(post=post)
                    else:
                        comment = ApprovedCommentFactory(post=post, moderated_by=staff_user)
                    
                    all_comments.append(comment)
    
    return {
        'users': all_users,
        'categories': all_categories,
        'posts': all_posts,
        'comments': all_comments,
        'tags': all_tags,
        'staff_user': staff_user,
        'super_user': super_user
    }


# Utility functions for common test scenarios
def create_user_with_blog():
    """Create a user with a complete blog setup"""
    user = UserFactory()
    category = CategoryFactory()
    
    # Create mix of published and draft posts
    published_posts = PostFactory.create_batch(5, author=user, category=category, status='published')
    draft_posts = DraftPostFactory.create_batch(2, author=user, category=category)
    
    # Add comments to published posts
    for post in published_posts:
        CommentFactory.create_batch(factory.Faker('random_int', min=1, max=4).generate(), post=post)
    
    return {
        'user': user,
        'category': category,
        'published_posts': published_posts,
        'draft_posts': draft_posts
    }


def create_moderation_scenario():
    """Create a scenario for testing comment moderation"""
    moderator = StaffUserFactory()
    post = PostFactory(status='published')
    
    # Create comments in different states
    pending_comments = PendingCommentFactory.create_batch(3, post=post)
    spam_comments = SpamCommentFactory.create_batch(2, post=post)
    approved_comments = ApprovedCommentFactory.create_batch(5, post=post, moderated_by=moderator)
    
    return {
        'moderator': moderator,
        'post': post,
        'pending_comments': pending_comments,
        'spam_comments': spam_comments,
        'approved_comments': approved_comments
    }


def create_performance_test_data():
    """Create large dataset for performance testing"""
    return create_blog_data(
        users=50,
        categories=10,
        posts_per_category=100,
        comments_per_post=10,
        tags=100
    )