from django.contrib import admin
from django.utils.html import format_html
from .models import EmailTemplate, Placeholder, TemplateAttachment


class TemplateAttachmentInline(admin.TabularInline):
    model = TemplateAttachment
    extra = 0
    readonly_fields = ('file_size', 'mime_type', 'uploaded_at')


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'is_active', 'created_by', 'created_at', 'placeholders_display')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'subject', 'description')
    readonly_fields = ('created_at', 'updated_at', 'version', 'parent_template', 'placeholders_display')
    inlines = [TemplateAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'body_html', 'body_plain')
        }),
        ('Versioning', {
            'fields': ('version', 'parent_template'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'placeholders_display'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def placeholders_display(self, obj):
        """Display extracted placeholders"""
        placeholders = obj.get_placeholders()
        if placeholders:
            return format_html(', '.join([f'<code>{{{{{p}}}}}</code>' for p in placeholders]))
        return '-'
    placeholders_display.short_description = 'Detected Placeholders'


@admin.register(Placeholder)
class PlaceholderAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_type', 'is_required', 'example_value', 'created_at')
    list_filter = ('data_type', 'is_required', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Placeholder Information', {
            'fields': ('name', 'description', 'data_type', 'is_required')
        }),
        ('Testing', {
            'fields': ('example_value',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
