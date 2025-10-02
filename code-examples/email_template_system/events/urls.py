from django.urls import path
from . import views

urlpatterns = [
    # Event Type URLs
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='event_create'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Event Trigger URLs
    path('triggers/', views.trigger_list, name='trigger_list'),
    path('triggers/<int:pk>/', views.trigger_detail, name='trigger_detail'),
    
    # API URLs
    path('api/trigger/', views.api_trigger_event, name='api_trigger_event'),
]
