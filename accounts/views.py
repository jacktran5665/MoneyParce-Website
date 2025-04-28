from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages

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
                error = 'Security answer is incorrect'
            elif password != password2:
                error = 'Passwords do not match'
            else:
                user.set_password(password)
                user.save()
                from django.contrib.auth import login
                login(request, user)
                from django.shortcuts import redirect
                return redirect('dashboard')
        except User.DoesNotExist:
            error = 'User not found'
        except Profile.DoesNotExist:
            error = 'Profile not found'
    template_data['error'] = error
    return render(request, 'accounts/forgot_password.html', template_data)


@login_required
def delete_account(request):
    if request.method == 'GET':
        return render(request, 'accounts/delete_account.html')

    elif request.method == 'POST':
        password = request.POST.get('password', '')
        confirmation = request.POST.get('confirmation', '')

        # Check if the password is correct and the confirmation text is "DELETE"
        if not check_password(password, request.user.password):
            messages.error(request, "Incorrect password. Please try again.")
            return render(request, 'accounts/delete_account.html')

        if confirmation != 'DELETE':
            messages.error(request, "Please type DELETE in all caps to confirm.")
            return render(request, 'accounts/delete_account.html')

        user = request.user

        logout(request)

        user.delete()

        return redirect('/')