from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # Template URLs
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/', views.template_detail, name='template_detail'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    path('templates/<int:pk>/preview/', views.template_preview, name='template_preview'),
    
    # Placeholder URLs
    path('placeholders/', views.placeholder_list, name='placeholder_list'),
    path('placeholders/create/', views.placeholder_create, name='placeholder_create'),
    path('placeholders/<int:pk>/edit/', views.placeholder_edit, name='placeholder_edit'),
    path('placeholders/<int:pk>/delete/', views.placeholder_delete, name='placeholder_delete'),
]
