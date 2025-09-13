"""
URL configuration for patterns demo app.
"""
from django.urls import path
from . import views

app_name = 'patterns_demo'

urlpatterns = [
    path('', views.PatternsIndexView.as_view(), name='index'),
    path('repository/', views.RepositoryDemoView.as_view(), name='repository_demo'),
    path('service/', views.ServiceDemoView.as_view(), name='service_demo'),
    path('factory/', views.FactoryDemoView.as_view(), name='factory_demo'),
    path('strategy/', views.StrategyDemoView.as_view(), name='strategy_demo'),
]