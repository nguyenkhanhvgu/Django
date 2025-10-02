from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from .models import EmailLog, SMTPConfiguration
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails with logging and retry support"""
    
    def __init__(self, smtp_config=None):
        """
        Initialize email service
        
        Args:
            smtp_config: SMTPConfiguration instance (optional, uses default if not provided)
        """
        if smtp_config:
            self.smtp_config = smtp_config
        else:
            self.smtp_config = SMTPConfiguration.objects.filter(is_default=True, is_active=True).first()
    
    def send_email(self, recipient, subject, body_html, body_plain='', 
                   event_type=None, event_trigger=None, template=None, 
                   attachments=None, request=None):
        """
        Send an email and log the result
        
        Args:
            recipient: Email address of recipient
            subject: Email subject
            body_html: HTML body content
            body_plain: Plain text body content (optional)
            event_type: EventType instance (optional)
            event_trigger: EventTrigger instance (optional)
            template: EmailTemplate instance (optional)
            attachments: List of file paths to attach (optional)
            request: HTTP request object for IP tracking (optional)
        
        Returns:
            EmailLog instance
        """
        # Create email log entry
        email_log = EmailLog.objects.create(
            event_type=event_type,
            event_trigger=event_trigger,
            template=template,
            recipient=recipient,
            subject=subject,
            body_html=body_html,
            body_plain=body_plain,
            delivery_status='queued',
            ip_address=self._get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else ''
        )
        
        try:
            # Update status to sending
            email_log.delivery_status = 'sending'
            email_log.save()
            
            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=body_plain or body_html,
                from_email=self.smtp_config.from_email if self.smtp_config else settings.DEFAULT_FROM_EMAIL,
                to=[recipient]
            )
            
            # Attach HTML alternative
            if body_html:
                email.attach_alternative(body_html, "text/html")
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    email.attach_file(attachment)
            
            # Send the email
            email.send()
            
            # Update log with success
            email_log.delivery_status = 'sent'
            email_log.save()
            
            logger.info(f"Email sent successfully to {recipient}: {subject}")
            
        except Exception as e:
            # Log the error
            email_log.delivery_status = 'failed'
            email_log.error_message = str(e)
            email_log.save()
            
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
        
        return email_log
    
    def retry_failed_email(self, email_log):
        """
        Retry sending a failed email
        
        Args:
            email_log: EmailLog instance to retry
        
        Returns:
            Updated EmailLog instance
        """
        if email_log.delivery_status not in ['failed', 'bounced']:
            logger.warning(f"Cannot retry email with status: {email_log.delivery_status}")
            return email_log
        
        email_log.retry_count += 1
        email_log.last_retry_at = timezone.now()
        email_log.save()
        
        return self.send_email(
            recipient=email_log.recipient,
            subject=email_log.subject,
            body_html=email_log.body_html,
            body_plain=email_log.body_plain,
            event_type=email_log.event_type,
            event_trigger=email_log.event_trigger,
            template=email_log.template
        )
    
    def _get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class EventEmailService:
    """Service for sending emails triggered by events"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    def process_event(self, event_trigger):
        """
        Process an event trigger and send the associated email
        
        Args:
            event_trigger: EventTrigger instance
        
        Returns:
            EmailLog instance or None if failed
        """
        try:
            event_type = event_trigger.event_type
            
            # Check if event type has a template
            if not event_type.template:
                logger.error(f"Event type {event_type.name} has no template assigned")
                event_trigger.status = 'failed'
                event_trigger.error_message = 'No template assigned to event type'
                event_trigger.save()
                return None
            
            # Get recipient from event data
            event_data = event_trigger.event_data
            recipient = event_data.get('recipient_email') or event_data.get('email')
            
            if not recipient:
                logger.error(f"No recipient email found in event data for {event_type.name}")
                event_trigger.status = 'failed'
                event_trigger.error_message = 'No recipient email in event data'
                event_trigger.save()
                return None
            
            # Render template with event data
            template = event_type.template
            rendered = template.render(event_data)
            
            # Update event trigger status
            event_trigger.status = 'processing'
            event_trigger.save()
            
            # Send email
            email_log = self.email_service.send_email(
                recipient=recipient,
                subject=rendered['subject'],
                body_html=rendered['body_html'],
                body_plain=rendered['body_plain'],
                event_type=event_type,
                event_trigger=event_trigger,
                template=template
            )
            
            # Update event trigger based on email result
            if email_log.delivery_status in ['sent', 'delivered']:
                event_trigger.status = 'completed'
            else:
                event_trigger.status = 'failed'
                event_trigger.error_message = email_log.error_message
            
            event_trigger.save()
            
            return email_log
            
        except Exception as e:
            logger.error(f"Error processing event trigger {event_trigger.id}: {str(e)}")
            event_trigger.status = 'failed'
            event_trigger.error_message = str(e)
            event_trigger.save()
            return None
