from django import forms
from .models import EventType, EventPlaceholder
from templates_manager.models import EmailTemplate


class EventTypeForm(forms.ModelForm):
    """Form for creating/editing event types"""
    
    class Meta:
        model = EventType
        fields = ['name', 'slug', 'description', 'template', 'is_active', 'trigger_method']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., User Registration'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., user-registration'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe when this event occurs'
            }),
            'template': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'trigger_method': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class TriggerEventForm(forms.Form):
    """Form for manually triggering an event"""
    
    event_type = forms.ModelChoiceField(
        queryset=EventType.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Event Type'
    )
    recipient_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'recipient@example.com'
        }),
        label='Recipient Email'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Will be populated dynamically based on selected event type
