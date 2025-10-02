from django.contrib import admin
from django.utils.html import format_html
from .models import EventType, EventPlaceholder, EventTrigger


class EventPlaceholderInline(admin.TabularInline):
    model = EventPlaceholder
    extra = 1
    autocomplete_fields = ['placeholder']


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'trigger_method', 'template', 'created_at')
    list_filter = ('is_active', 'trigger_method', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [EventPlaceholderInline]
    
    fieldsets = (
        ('Event Information', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Configuration', {
            'fields': ('template', 'trigger_method')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EventTrigger)
class EventTriggerAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'status', 'triggered_by', 'triggered_at', 'status_badge')
    list_filter = ('status', 'event_type', 'triggered_at')
    search_fields = ('event_type__name',)
    readonly_fields = ('triggered_at', 'event_data', 'error_message')
    
    fieldsets = (
        ('Event Information', {
            'fields': ('event_type', 'triggered_by', 'triggered_at')
        }),
        ('Event Data', {
            'fields': ('event_data',)
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
    )
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        # Event triggers should be created programmatically
        return False
