from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_history, name='transactions_history'),
    path('delete/', views.delete_transaction, name='transactions_delete'),
]