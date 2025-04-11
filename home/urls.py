from django.urls import path 
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('about-us/', views.about_us, name='about_us'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('homepage/', views.homepage, name='homepage'),
]