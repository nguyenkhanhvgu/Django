"""
Custom Django signals for the blog application.
"""
import django.dispatch

# Custom signals
post_viewed = django.dispatch.Signal()
post_liked = django.dispatch.Signal()
post_shared = django.dispatch.Signal()
comment_added = django.dispatch.Signal()
user_mentioned = django.dispatch.Signal()