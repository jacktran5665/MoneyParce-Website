from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'

    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/register.html', {'template_data': template_data})

    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            budget = form.cleaned_data['budget']
            from home.models import Profile
            Profile.objects.create(user=user, budget=budget)
            login(request, user)
            return redirect('dashboard')
        else:
            template_data['form'] = form
            return render(request, 'accounts/register.html', {'template_data': template_data})

def forgot_password(request):
    from django.contrib.auth.models import User
    from home.models import Profile
    from django.contrib.auth.hashers import make_password
    template_data = {}
    template_data['title'] = 'Forgot Password'
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        budget = request.POST.get('budget')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        try:
            user = User.objects.get(username=username)
            profile = Profile.objects.get(user=user)
            if str(profile.budget) != str(budget):
                error = 'Security answer is incorrect.'
            elif password != password2:
                error = 'Passwords do not match.'
            else:
                user.set_password(password)
                user.save()
                from django.contrib.auth import login
                login(request, user)
                from django.shortcuts import redirect
                return redirect('dashboard')
        except User.DoesNotExist:
            error = 'User not found.'
        except Profile.DoesNotExist:
            error = 'Profile not found.'
    template_data['error'] = error
    return render(request, 'home/forgot_password.html', template_data)

