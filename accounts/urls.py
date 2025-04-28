from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.signup, name='accounts.signup'),
    # Add this new URL pattern:
    path('delete-account/', views.delete_account, name='delete_account'),
]