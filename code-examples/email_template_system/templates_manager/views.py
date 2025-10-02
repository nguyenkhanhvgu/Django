from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import EmailTemplate, Placeholder
from .forms import EmailTemplateForm, TemplatePreviewForm, PlaceholderForm


def index(request):
    """Dashboard/home page"""
    context = {
        'total_templates': EmailTemplate.objects.filter(is_active=True).count(),
        'total_placeholders': Placeholder.objects.count(),
        'recent_templates': EmailTemplate.objects.filter(is_active=True)[:5],
    }
    return render(request, 'templates_manager/index.html', context)


@login_required
def template_list(request):
    """List all email templates"""
    templates = EmailTemplate.objects.all()
    return render(request, 'templates_manager/template_list.html', {'templates': templates})


@login_required
def template_create(request):
    """Create a new email template"""
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.created_by = request.user
            template.save()
            messages.success(request, f'Template "{template.name}" created successfully!')
            return redirect('template_detail', pk=template.pk)
    else:
        form = EmailTemplateForm()
    
    return render(request, 'templates_manager/template_form.html', {
        'form': form,
        'action': 'Create'
    })


@login_required
def template_detail(request, pk):
    """View template details"""
    template = get_object_or_404(EmailTemplate, pk=pk)
    placeholders = template.get_placeholders()
    
    return render(request, 'templates_manager/template_detail.html', {
        'template': template,
        'placeholders': placeholders
    })


@login_required
def template_edit(request, pk):
    """Edit an existing template"""
    template = get_object_or_404(EmailTemplate, pk=pk)
    
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, f'Template "{template.name}" updated successfully!')
            return redirect('template_detail', pk=template.pk)
    else:
        form = EmailTemplateForm(instance=template)
    
    return render(request, 'templates_manager/template_form.html', {
        'form': form,
        'template': template,
        'action': 'Edit'
    })


@login_required
def template_preview(request, pk):
    """Preview template with test data"""
    template = get_object_or_404(EmailTemplate, pk=pk)
    placeholders = template.get_placeholders()
    
    preview_data = None
    if request.method == 'POST':
        form = TemplatePreviewForm(request.POST, placeholders=placeholders)
        if form.is_valid():
            # Get placeholder values from form
            context_data = {key: value for key, value in form.cleaned_data.items() if value}
            
            # Get example values for missing placeholders
            for placeholder_name in placeholders:
                if placeholder_name not in context_data:
                    try:
                        placeholder = Placeholder.objects.get(name=placeholder_name)
                        context_data[placeholder_name] = placeholder.example_value or f'[{placeholder_name}]'
                    except Placeholder.DoesNotExist:
                        context_data[placeholder_name] = f'[{placeholder_name}]'
            
            preview_data = template.render(context_data)
    else:
        form = TemplatePreviewForm(placeholders=placeholders)
        
        # Pre-fill with example values
        initial = {}
        for placeholder_name in placeholders:
            try:
                placeholder = Placeholder.objects.get(name=placeholder_name)
                initial[placeholder_name] = placeholder.example_value
            except Placeholder.DoesNotExist:
                pass
        
        form = TemplatePreviewForm(initial=initial, placeholders=placeholders)
    
    return render(request, 'templates_manager/template_preview.html', {
        'template': template,
        'form': form,
        'preview_data': preview_data
    })


@login_required
def template_delete(request, pk):
    """Delete a template"""
    template = get_object_or_404(EmailTemplate, pk=pk)
    
    if request.method == 'POST':
        template_name = template.name
        template.delete()
        messages.success(request, f'Template "{template_name}" deleted successfully!')
        return redirect('template_list')
    
    return render(request, 'templates_manager/template_confirm_delete.html', {
        'template': template
    })


# Placeholder views

@login_required
def placeholder_list(request):
    """List all placeholders"""
    placeholders = Placeholder.objects.all()
    return render(request, 'templates_manager/placeholder_list.html', {
        'placeholders': placeholders
    })


@login_required
def placeholder_create(request):
    """Create a new placeholder"""
    if request.method == 'POST':
        form = PlaceholderForm(request.POST)
        if form.is_valid():
            placeholder = form.save()
            messages.success(request, f'Placeholder "{placeholder.name}" created successfully!')
            return redirect('placeholder_list')
    else:
        form = PlaceholderForm()
    
    return render(request, 'templates_manager/placeholder_form.html', {
        'form': form,
        'action': 'Create'
    })


@login_required
def placeholder_edit(request, pk):
    """Edit a placeholder"""
    placeholder = get_object_or_404(Placeholder, pk=pk)
    
    if request.method == 'POST':
        form = PlaceholderForm(request.POST, instance=placeholder)
        if form.is_valid():
            form.save()
            messages.success(request, f'Placeholder "{placeholder.name}" updated successfully!')
            return redirect('placeholder_list')
    else:
        form = PlaceholderForm(instance=placeholder)
    
    return render(request, 'templates_manager/placeholder_form.html', {
        'form': form,
        'placeholder': placeholder,
        'action': 'Edit'
    })


@login_required
def placeholder_delete(request, pk):
    """Delete a placeholder"""
    placeholder = get_object_or_404(Placeholder, pk=pk)
    
    if request.method == 'POST':
        placeholder_name = placeholder.name
        placeholder.delete()
        messages.success(request, f'Placeholder "{placeholder_name}" deleted successfully!')
        return redirect('placeholder_list')
    
    return render(request, 'templates_manager/placeholder_confirm_delete.html', {
        'placeholder': placeholder
    })
