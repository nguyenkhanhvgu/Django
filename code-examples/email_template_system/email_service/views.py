from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import csv
from .models import EmailLog


@login_required
def email_log_list(request):
    """List all email logs with filters"""
    logs = EmailLog.objects.all()
    
    # Filter by delivery status
    status = request.GET.get('status')
    if status:
        logs = logs.filter(delivery_status=status)
    
    # Filter by recipient
    recipient = request.GET.get('recipient')
    if recipient:
        logs = logs.filter(recipient__icontains=recipient)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        logs = logs.filter(sent_at__gte=date_from)
    if date_to:
        logs = logs.filter(sent_at__lte=date_to)
    
    # Get statistics
    stats = {
        'total': EmailLog.objects.count(),
        'sent': EmailLog.objects.filter(delivery_status='sent').count(),
        'failed': EmailLog.objects.filter(delivery_status='failed').count(),
        'queued': EmailLog.objects.filter(delivery_status='queued').count(),
    }
    
    return render(request, 'email_service/email_log_list.html', {
        'logs': logs[:100],  # Limit to 100 for performance
        'stats': stats
    })


@login_required
def email_log_detail(request, pk):
    """View email log details"""
    log = get_object_or_404(EmailLog, pk=pk)
    
    return render(request, 'email_service/email_log_detail.html', {
        'log': log
    })


@login_required
def email_log_export(request):
    """Export email logs to CSV"""
    # Get filtered logs
    logs = EmailLog.objects.all()
    
    # Apply filters from GET parameters
    status = request.GET.get('status')
    if status:
        logs = logs.filter(delivery_status=status)
    
    recipient = request.GET.get('recipient')
    if recipient:
        logs = logs.filter(recipient__icontains=recipient)
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        logs = logs.filter(sent_at__gte=date_from)
    if date_to:
        logs = logs.filter(sent_at__lte=date_to)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="email_logs.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Recipient', 'Subject', 'Status', 'Sent At',
        'Event Type', 'Template', 'Retry Count', 'Error Message'
    ])
    
    for log in logs:
        writer.writerow([
            log.id,
            log.recipient,
            log.subject,
            log.delivery_status,
            log.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            log.event_type.name if log.event_type else '',
            log.template.name if log.template else '',
            log.retry_count,
            log.error_message
        ])
    
    return response


@login_required
def email_log_retry(request, pk):
    """Retry sending a failed email"""
    log = get_object_or_404(EmailLog, pk=pk)
    
    if log.delivery_status not in ['failed', 'bounced']:
        messages.warning(request, 'Can only retry failed or bounced emails.')
        return redirect('email_log_detail', pk=pk)
    
    if request.method == 'POST':
        from .services import EmailService
        email_service = EmailService()
        new_log = email_service.retry_failed_email(log)
        
        if new_log.delivery_status in ['sent', 'delivered']:
            messages.success(request, 'Email resent successfully!')
        else:
            messages.error(request, f'Failed to resend email: {new_log.error_message}')
        
        return redirect('email_log_detail', pk=new_log.pk)
    
    return render(request, 'email_service/email_log_retry.html', {
        'log': log
    })


@login_required
def dashboard(request):
    """Email service dashboard with statistics"""
    # Get date range (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get statistics
    total_emails = EmailLog.objects.count()
    recent_emails = EmailLog.objects.filter(sent_at__gte=start_date)
    
    stats = {
        'total_emails': total_emails,
        'sent': EmailLog.objects.filter(delivery_status='sent').count(),
        'failed': EmailLog.objects.filter(delivery_status='failed').count(),
        'recent_count': recent_emails.count(),
    }
    
    # Get recent logs
    recent_logs = EmailLog.objects.all()[:10]
    
    # Get status breakdown
    status_breakdown = EmailLog.objects.values('delivery_status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return render(request, 'email_service/dashboard.html', {
        'stats': stats,
        'recent_logs': recent_logs,
        'status_breakdown': status_breakdown
    })
