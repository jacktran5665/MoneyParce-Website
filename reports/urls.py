from django.urls import path
from . import views

urlpatterns = [
    path('budget-summary/', views.budget_chart, name='budget_summary'),
]