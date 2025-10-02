from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='email_dashboard'),
    path('logs/', views.email_log_list, name='email_log_list'),
    path('logs/<int:pk>/', views.email_log_detail, name='email_log_detail'),
    path('logs/<int:pk>/retry/', views.email_log_retry, name='email_log_retry'),
    path('logs/export/', views.email_log_export, name='email_log_export'),
]
