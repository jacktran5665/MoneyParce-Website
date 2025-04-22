from django.shortcuts import render
from .forms import CustomUserCreationForm
from django.shortcuts import redirect
def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/register.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
        else:
            template_data['form'] = form
            return render(request, 'accounts/register.html',
                {'template_data': template_data})
