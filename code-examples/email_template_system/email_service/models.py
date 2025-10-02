from django.db import models
from events.models import EventType, EventTrigger
from templates_manager.models import EmailTemplate


class EmailLog(models.Model):
    """Log of all sent emails"""
    
    # Event information
    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True, blank=True)
    event_trigger = models.ForeignKey(EventTrigger, on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True)
    
    # Email details
    recipient = models.EmailField()
    subject = models.CharField(max_length=500)
    body_html = models.TextField()
    body_plain = models.TextField(blank=True)
    
    # Sending details
    sent_at = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(
        max_length=50,
        choices=[
            ('queued', 'Queued'),
            ('sending', 'Sending'),
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('failed', 'Failed'),
            ('bounced', 'Bounced'),
        ],
        default='queued'
    )
    
    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    last_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Additional metadata
    smtp_message_id = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        indexes = [
            models.Index(fields=['-sent_at']),
            models.Index(fields=['recipient']),
            models.Index(fields=['delivery_status']),
        ]
    
    def __str__(self):
        return f"Email to {self.recipient} - {self.delivery_status}"


class EmailRetryPolicy(models.Model):
    """Configuration for email retry policies"""
    
    name = models.CharField(max_length=255, unique=True)
    max_retries = models.IntegerField(default=3, help_text="Maximum number of retry attempts")
    retry_delay_seconds = models.IntegerField(default=300, help_text="Delay between retries in seconds")
    backoff_multiplier = models.FloatField(default=2.0, help_text="Multiplier for exponential backoff")
    
    # Which statuses should trigger a retry
    retry_on_statuses = models.JSONField(
        default=list,
        help_text="List of delivery statuses that should trigger a retry"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Email Retry Policy'
        verbose_name_plural = 'Email Retry Policies'
    
    def __str__(self):
        return self.name


class SMTPConfiguration(models.Model):
    """SMTP server configuration"""
    
    name = models.CharField(max_length=255, unique=True)
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True, help_text="Stored encrypted in production")
    from_email = models.EmailField()
    
    # Settings
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    timeout = models.IntegerField(default=30, help_text="Connection timeout in seconds")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'SMTP Configuration'
        verbose_name_plural = 'SMTP Configurations'
    
    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"
    
    def save(self, *args, **kwargs):
        # Ensure only one default configuration
        if self.is_default:
            SMTPConfiguration.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
