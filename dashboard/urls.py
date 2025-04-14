from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard_view, name='dashboard.index'),
    path('dashboard/', views.dashboard, name='dashboard')
]