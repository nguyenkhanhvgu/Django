from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import EventType, EventTrigger
from .forms import EventTypeForm, TriggerEventForm
from email_service.services import EventEmailService


@login_required
def event_list(request):
    """List all event types"""
    events = EventType.objects.all()
    return render(request, 'events/event_list.html', {'events': events})


@login_required
def event_create(request):
    """Create a new event type"""
    if request.method == 'POST':
        form = EventTypeForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f'Event type "{event.name}" created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventTypeForm()
    
    return render(request, 'events/event_form.html', {
        'form': form,
        'action': 'Create'
    })


@login_required
def event_detail(request, pk):
    """View event type details"""
    event = get_object_or_404(EventType, pk=pk)
    recent_triggers = event.triggers.all()[:10]
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'recent_triggers': recent_triggers
    })


@login_required
def event_edit(request, pk):
    """Edit an event type"""
    event = get_object_or_404(EventType, pk=pk)
    
    if request.method == 'POST':
        form = EventTypeForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event type "{event.name}" updated successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventTypeForm(instance=event)
    
    return render(request, 'events/event_form.html', {
        'form': form,
        'event': event,
        'action': 'Edit'
    })


@login_required
def event_delete(request, pk):
    """Delete an event type"""
    event = get_object_or_404(EventType, pk=pk)
    
    if request.method == 'POST':
        event_name = event.name
        event.delete()
        messages.success(request, f'Event type "{event_name}" deleted successfully!')
        return redirect('event_list')
    
    return render(request, 'events/event_confirm_delete.html', {
        'event': event
    })


@login_required
def trigger_list(request):
    """List all event triggers"""
    triggers = EventTrigger.objects.all()
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        triggers = triggers.filter(status=status)
    
    # Filter by event type if provided
    event_type = request.GET.get('event_type')
    if event_type:
        triggers = triggers.filter(event_type__slug=event_type)
    
    return render(request, 'events/trigger_list.html', {
        'triggers': triggers,
        'event_types': EventType.objects.all()
    })


@login_required
def trigger_detail(request, pk):
    """View trigger details"""
    trigger = get_object_or_404(EventTrigger, pk=pk)
    
    # Get related email log if exists
    email_log = None
    if hasattr(trigger, 'emaillog_set'):
        email_log = trigger.emaillog_set.first()
    
    return render(request, 'events/trigger_detail.html', {
        'trigger': trigger,
        'email_log': email_log
    })


# API endpoints for triggering events

@csrf_exempt
@require_http_methods(["POST"])
def api_trigger_event(request):
    """
    API endpoint to trigger an event
    
    POST /api/trigger/
    {
        "event_slug": "user-registration",
        "data": {
            "recipient_email": "user@example.com",
            "CustomerName": "John Doe",
            ...
        }
    }
    """
    try:
        # Parse request body
        data = json.loads(request.body)
        event_slug = data.get('event_slug')
        event_data = data.get('data', {})
        
        # Validate event type
        try:
            event_type = EventType.objects.get(slug=event_slug, is_active=True)
        except EventType.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Event type "{event_slug}" not found or inactive'
            }, status=404)
        
        # Create event trigger
        trigger = EventTrigger.objects.create(
            event_type=event_type,
            event_data=event_data,
            status='pending'
        )
        
        # Process the event (send email)
        email_service = EventEmailService()
        email_log = email_service.process_event(trigger)
        
        if email_log and email_log.delivery_status in ['sent', 'delivered']:
            return JsonResponse({
                'success': True,
                'trigger_id': trigger.id,
                'email_log_id': email_log.id,
                'status': trigger.status
            })
        else:
            return JsonResponse({
                'success': False,
                'trigger_id': trigger.id,
                'error': trigger.error_message
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
