from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from .models import Profile
import re

def index(request):
    return render(request, 'home/index.html')

def dashboard(request):
    return render(request, 'accounts/dashboard.html')  # Updated path

def about_us(request):
    return render(request, 'home/about_us.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        budget = request.POST.get('security_question')

        if password != confirm_password:
            return render(request, 'accounts/register.html', {'error': 'Passwords do not match'})

        # Password validation
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d{6,})(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            return render(request, 'accounts/register.html', {'error': 'Password must have at least 1 uppercase, 1 lowercase, 6 numbers, and 1 symbol'})

        # Create user
        user = User.objects.create_user(username=username, password=password)

        # Create profile
        Profile.objects.create(user=user, budget=budget)

        return redirect('/dashboard')
    return render(request, 'accounts/register.html')
