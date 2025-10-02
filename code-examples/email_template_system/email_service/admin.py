from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import EmailLog, EmailRetryPolicy, SMTPConfiguration


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'subject_short', 'delivery_status', 'status_badge', 'sent_at', 'retry_count')
    list_filter = ('delivery_status', 'sent_at', 'event_type')
    search_fields = ('recipient', 'subject', 'smtp_message_id')
    readonly_fields = ('sent_at', 'last_retry_at', 'event_type', 'event_trigger', 'template',
                      'subject', 'body_html', 'body_plain', 'smtp_message_id', 'ip_address', 'user_agent')
    date_hierarchy = 'sent_at'
    
    fieldsets = (
        ('Email Information', {
            'fields': ('recipient', 'subject', 'delivery_status')
        }),
        ('Content', {
            'fields': ('body_html', 'body_plain'),
            'classes': ('collapse',)
        }),
        ('Event Information', {
            'fields': ('event_type', 'event_trigger', 'template'),
            'classes': ('collapse',)
        }),
        ('Delivery Details', {
            'fields': ('sent_at', 'retry_count', 'last_retry_at', 'error_message')
        }),
        ('Technical Details', {
            'fields': ('smtp_message_id', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def subject_short(self, obj):
        """Display truncated subject"""
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
    subject_short.short_description = 'Subject'
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'queued': '#6c757d',
            'sending': '#17a2b8',
            'sent': '#28a745',
            'delivered': '#28a745',
            'failed': '#dc3545',
            'bounced': '#ffc107',
        }
        color = colors.get(obj.delivery_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.delivery_status.upper()
        )
    status_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        # Email logs should be created by the system
        return False


@admin.register(EmailRetryPolicy)
class EmailRetryPolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_retries', 'retry_delay_seconds', 'backoff_multiplier', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Policy Information', {
            'fields': ('name', 'is_active')
        }),
        ('Retry Configuration', {
            'fields': ('max_retries', 'retry_delay_seconds', 'backoff_multiplier', 'retry_on_statuses')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SMTPConfiguration)
class SMTPConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'from_email', 'is_active', 'is_default')
    list_filter = ('is_active', 'is_default', 'use_tls', 'use_ssl')
    search_fields = ('name', 'host', 'from_email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Configuration Name', {
            'fields': ('name', 'is_active', 'is_default')
        }),
        ('SMTP Server', {
            'fields': ('host', 'port', 'use_tls', 'use_ssl', 'timeout')
        }),
        ('Authentication', {
            'fields': ('username', 'password', 'from_email')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make password field use password widget
        if 'password' in form.base_fields:
            form.base_fields['password'].widget.attrs['type'] = 'password'
        return form
