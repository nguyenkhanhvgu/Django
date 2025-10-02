from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import re


class EmailTemplate(models.Model):
    """Email template with placeholder support"""
    
    name = models.CharField(max_length=255, unique=True, help_text="Unique template name")
    subject = models.CharField(max_length=500, help_text="Email subject (supports {{placeholders}})")
    body_html = models.TextField(help_text="HTML email body (supports {{placeholders}})")
    body_plain = models.TextField(blank=True, help_text="Plain text email body (optional)")
    
    # Metadata
    description = models.TextField(blank=True, help_text="Template description")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Versioning support
    version = models.IntegerField(default=1)
    parent_template = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='versions', help_text="Previous version of this template")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
    
    def get_placeholders(self):
        """Extract all placeholders from subject and body"""
        pattern = r'\{\{(\w+)\}\}'
        placeholders = set()
        
        # Extract from subject
        placeholders.update(re.findall(pattern, self.subject))
        
        # Extract from HTML body
        placeholders.update(re.findall(pattern, self.body_html))
        
        # Extract from plain text body
        if self.body_plain:
            placeholders.update(re.findall(pattern, self.body_plain))
        
        return list(placeholders)
    
    def render(self, context_data):
        """Render template with provided context data"""
        subject = self.subject
        body_html = self.body_html
        body_plain = self.body_plain or ''
        
        # Replace placeholders
        for key, value in context_data.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            body_html = body_html.replace(placeholder, str(value))
            if body_plain:
                body_plain = body_plain.replace(placeholder, str(value))
        
        return {
            'subject': subject,
            'body_html': body_html,
            'body_plain': body_plain
        }
    
    def create_new_version(self, user=None):
        """Create a new version of this template"""
        new_template = EmailTemplate.objects.create(
            name=self.name,
            subject=self.subject,
            body_html=self.body_html,
            body_plain=self.body_plain,
            description=self.description,
            created_by=user or self.created_by,
            is_active=self.is_active,
            version=self.version + 1,
            parent_template=self
        )
        return new_template


class Placeholder(models.Model):
    """Placeholder definition for email templates"""
    
    name = models.CharField(max_length=100, unique=True, help_text="Placeholder name (without braces)")
    description = models.TextField(help_text="Description of what this placeholder represents")
    example_value = models.CharField(max_length=255, blank=True, help_text="Example value for preview")
    data_type = models.CharField(
        max_length=50, 
        choices=[
            ('string', 'String'),
            ('number', 'Number'),
            ('date', 'Date'),
            ('datetime', 'DateTime'),
            ('email', 'Email'),
            ('url', 'URL'),
        ],
        default='string'
    )
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Placeholder'
        verbose_name_plural = 'Placeholders'
    
    def __str__(self):
        return f"{{{{{self.name}}}}}"


class TemplateAttachment(models.Model):
    """File attachments for email templates"""
    
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='template_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Template Attachment'
        verbose_name_plural = 'Template Attachments'
    
    def __str__(self):
        return f"{self.filename} ({self.template.name})"
