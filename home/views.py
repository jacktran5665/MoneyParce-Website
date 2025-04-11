from django.shortcuts import render, redirect

def index(request):
    return render(request, 'home/index.html')

def register(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            # Assume user registration logic here (e.g., create user in the database)
            return redirect('homepage')  # Redirect to homepage after successful registration
        else:
            return render(request, 'home/register.html', {'error': 'Passwords do not match'})
    return render(request, 'home/register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Placeholder authentication logic here (replace with actual login logic)
        if username == 'valid_user' and password == 'valid_pass':  # Actual authentication needed
            return redirect('home:homepage')  # Redirect to homepage after successful login
        else:
            return render(request, 'home/login.html', {'error': 'Invalid username or password'})
    return render(request, 'home/login.html')

def homepage(request):
    return render(request, 'home/homepage.html')

def about_us(request):
    return render(request, 'home/about_us.html')
