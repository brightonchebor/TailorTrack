from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        email = request.POST.get('email', '').strip()
        
        # Validate input fields
        if not username:
            messages.error(request, 'Username is required')
            return render(request, 'accounts/register.html')
        
        if not email:
            messages.error(request, 'Email is required')
            return render(request, 'accounts/register.html')
        
        if not password:
            messages.error(request, 'Password is required')
            return render(request, 'accounts/register.html')
        
        if not confirm_password:
            messages.error(request, 'Password confirmation is required')
            return render(request, 'accounts/register.html')
        
        # Validate password length
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
            return render(request, 'accounts/register.html')
        
        # Validate username length and characters
        if len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters long')
            return render(request, 'accounts/register.html')
        
        if not username.isalnum() and '_' not in username:
            messages.error(request, 'Username can only contain letters, numbers, and underscores')
            return render(request, 'accounts/register.html')
        
        # Check password match
        if password != confirm_password:
            messages.error(request, 'Password mismatch. Ensure both fields are identical')
            return render(request, 'accounts/register.html')
        
        try:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different username.')
                return render(request, 'accounts/register.html')
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists. Please use a different email.')
                return render(request, 'accounts/register.html')
            
            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email
            )
            
            messages.success(request, 'Your profile has been set up! Login and explore your dashboard.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'An error occurred while creating your account: {str(e)}')
            return render(request, 'accounts/register.html')
    
    # GET request - show registration form
    return render(request, 'accounts/register.html')

def login_view(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user is not None:
            login(request, user)
            messages.success(
                request,
                'You are now logged in'
            )
            return redirect('dashboard')
        else:
            messages.error(
                request,
                'Invalid login credentials'
            )    
    return render(request, 'accounts/login.html', context={})

def logout_view(request):
    logout(request)
    return redirect('dashboard')
    