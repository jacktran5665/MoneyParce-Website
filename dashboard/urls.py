from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('create_link_token/', views.create_link_token, name='create_link_token'),
    path('exchange_public_token/', views.exchange_public_token, name='exchange_public_token'),
    path('fetch_transactions/', views.fetch_transactions, name='fetch_transactions'),
]