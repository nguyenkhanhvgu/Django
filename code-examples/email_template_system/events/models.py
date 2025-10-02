from django.db import models
from django.contrib.auth.models import User
from templates_manager.models import EmailTemplate, Placeholder
import json


class EventType(models.Model):
    """Define types of events that can trigger emails"""
    
    name = models.CharField(max_length=255, unique=True, help_text="Event name (e.g., 'User Registration')")
    slug = models.SlugField(max_length=255, unique=True, help_text="URL-safe event identifier")
    description = models.TextField(help_text="Description of when this event occurs")
    
    # Associated template
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='events', help_text="Email template to use for this event")
    
    # Event settings
    is_active = models.BooleanField(default=True)
    trigger_method = models.CharField(
        max_length=50,
        choices=[
            ('api', 'API Call'),
            ('manual', 'Manual Trigger'),
            ('scheduled', 'Scheduled'),
            ('internal', 'Internal System Event'),
        ],
        default='api'
    )
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Event Type'
        verbose_name_plural = 'Event Types'
    
    def __str__(self):
        return self.name


class EventPlaceholder(models.Model):
    """Links placeholders to specific event types"""
    
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='placeholders')
    placeholder = models.ForeignKey(Placeholder, on_delete=models.CASCADE)
    is_required = models.BooleanField(default=True)
    default_value = models.CharField(max_length=255, blank=True, help_text="Default value if not provided")
    
    class Meta:
        unique_together = ('event_type', 'placeholder')
        verbose_name = 'Event Placeholder'
        verbose_name_plural = 'Event Placeholders'
    
    def __str__(self):
        return f"{self.event_type.name} - {self.placeholder.name}"


class EventTrigger(models.Model):
    """Log of triggered events"""
    
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='triggers')
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    triggered_at = models.DateTimeField(auto_now_add=True)
    
    # Event data
    event_data = models.JSONField(help_text="JSON data passed with the event")
    
    # Status tracking
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-triggered_at']
        verbose_name = 'Event Trigger'
        verbose_name_plural = 'Event Triggers'
    
    def __str__(self):
        return f"{self.event_type.name} - {self.triggered_at.strftime('%Y-%m-%d %H:%M')}"
