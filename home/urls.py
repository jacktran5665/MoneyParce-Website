from django.urls import path
from . import views

from accounts.views import forgot_password

urlpatterns = [
    path('', views.index, name='index'),
    path('about-us/', views.about_us, name='about_us'),
    path('forgot-password/', forgot_password, name='forgot_password'),
]
