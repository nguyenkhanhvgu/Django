from django import forms
from .models import EmailTemplate, Placeholder


class EmailTemplateForm(forms.ModelForm):
    """Form for creating/editing email templates"""
    
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body_html', 'body_plain', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter template name'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email subject (use {{PlaceholderName}} for dynamic content)'
            }),
            'body_html': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'HTML email body (use {{PlaceholderName}} for dynamic content)'
            }),
            'body_plain': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Plain text email body (optional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description of this template'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class TemplatePreviewForm(forms.Form):
    """Form for previewing templates with test data"""
    
    def __init__(self, *args, placeholders=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically create fields for each placeholder
        if placeholders:
            for placeholder in placeholders:
                self.fields[placeholder] = forms.CharField(
                    label=placeholder,
                    required=False,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': f'Value for {{{{{placeholder}}}}}'
                    })
                )


class PlaceholderForm(forms.ModelForm):
    """Form for creating/editing placeholders"""
    
    class Meta:
        model = Placeholder
        fields = ['name', 'description', 'data_type', 'is_required', 'example_value']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., CustomerName'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe what this placeholder represents'
            }),
            'data_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'example_value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., John Doe'
            }),
        }
