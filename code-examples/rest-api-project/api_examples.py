#!/usr/bin/env python
"""
Example script demonstrating how to use the Blog API.
Run this after setting up the project and creating a superuser.
"""

import requests
import json

# API base URL
BASE_URL = 'http://localhost:8000/api'

def register_user():
    """Register a new user."""
    url = f'{BASE_URL}/auth/register/'
    data = {
        'username': 'apiuser',
        'email': 'apiuser@example.com',
        'password': 'securepass123',
        'password_confirm': 'securepass123',
        'first_name': 'API',
        'last_name': 'User'
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print("✅ User registered successfully")
        return response.json()['token']
    else:
        print(f"❌ Registration failed: {response.json()}")
        return None

def login_user():
    """Login existing user."""
    url = f'{BASE_URL}/auth/login/'
    data = {
        'username': 'apiuser',
        'password': 'securepass123'
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("✅ Login successful")
        return response.json()['token']
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def create_category(token):
    """Create a new category."""
    url = f'{BASE_URL}/categories/'
    headers = {'Authorization': f'Token {token}'}
    data = {
        'name': 'Technology',
        'description': 'Posts about technology and programming'
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print("✅ Category created successfully")
        return response.json()['id']
    else:
        print(f"❌ Category creation failed: {response.json()}")
        return None

def create_post(token, category_id):
    """Create a new blog post."""
    url = f'{BASE_URL}/posts/'
    headers = {'Authorization': f'Token {token}'}
    data = {
        'title': 'Getting Started with Django REST Framework',
        'content': '''Django REST Framework (DRF) is a powerful toolkit for building Web APIs. 
        In this post, we'll explore the key concepts and features that make DRF an excellent 
        choice for API development. We'll cover serializers, viewsets, authentication, and 
        permissions. This comprehensive guide will help you understand how to build robust 
        and scalable APIs with Django.''',
        'category': category_id,
        'status': 'published'
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print("✅ Post created successfully")
        return response.json()['id']
    else:
        print(f"❌ Post creation failed: {response.json()}")
        return None

def get_posts():
    """Get all posts."""
    url = f'{BASE_URL}/posts/'
    response = requests.get(url)
    
    if response.status_code == 200:
        posts = response.json()['results']
        print(f"✅ Retrieved {len(posts)} posts")
        for post in posts:
            print(f"  - {post['title']} by {post['author']['username']}")
        return posts
    else:
        print(f"❌ Failed to get posts: {response.json()}")
        return []

def search_posts(query):
    """Search posts by title or content."""
    url = f'{BASE_URL}/posts/'
    params = {'search': query}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        posts = response.json()['results']
        print(f"✅ Found {len(posts)} posts matching '{query}'")
        return posts
    else:
        print(f"❌ Search failed: {response.json()}")
        return []

def create_comment(token, post_id):
    """Create a comment on a post."""
    url = f'{BASE_URL}/posts/{post_id}/comments/'
    headers = {'Authorization': f'Token {token}'}
    data = {
        'content': 'Great post! Very helpful for beginners.'
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print("✅ Comment created successfully")
        return response.json()['id']
    else:
        print(f"❌ Comment creation failed: {response.json()}")
        return None

def like_post(token, post_id):
    """Like a post."""
    url = f'{BASE_URL}/posts/{post_id}/like/'
    headers = {'Authorization': f'Token {token}'}
    
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(f"✅ Post {response.json()['status']}")
        return True
    else:
        print(f"❌ Like failed: {response.json()}")
        return False

def get_post_stats(post_id):
    """Get statistics for a post."""
    url = f'{BASE_URL}/posts/{post_id}/stats/'
    
    response = requests.get(url)
    if response.status_code == 200:
        stats = response.json()
        print("✅ Post statistics:")
        print(f"  - Views: {stats['views_count']}")
        print(f"  - Likes: {stats['likes_count']}")
        print(f"  - Comments: {stats['comments_count']}")
        print(f"  - Reading time: {stats['reading_time']} minutes")
        return stats
    else:
        print(f"❌ Failed to get stats: {response.json()}")
        return None

def main():
    """Main function to demonstrate API usage."""
    print("🚀 Django REST Framework API Demo")
    print("=" * 40)
    
    # Try to login first, if that fails, register
    token = login_user()
    if not token:
        token = register_user()
    
    if not token:
        print("❌ Could not authenticate. Exiting.")
        return
    
    # Create a category (might fail if user is not staff)
    category_id = create_category(token)
    if not category_id:
        # Try to get existing categories
        response = requests.get(f'{BASE_URL}/categories/')
        if response.status_code == 200 and response.json()['results']:
            category_id = response.json()['results'][0]['id']
            print(f"✅ Using existing category ID: {category_id}")
    
    if category_id:
        # Create a post
        post_id = create_post(token, category_id)
        
        if post_id:
            # Get all posts
            get_posts()
            
            # Search posts
            search_posts('Django')
            
            # Create a comment
            create_comment(token, post_id)
            
            # Like the post
            like_post(token, post_id)
            
            # Get post statistics
            get_post_stats(post_id)
    
    print("\n✅ API demo completed!")
    print("Visit http://localhost:8000/api/docs/ for interactive documentation")

if __name__ == '__main__':
    main()