from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        email = request.POST['email']
        
        if password == confirm_password:
            try:
                # Check if username already exists
                if User.objects.filter(username=username).exists():
                    messages.error(request, 'Username already exists. Please choose a different username.')
                    return redirect('register')
                
                # Check if email already exists
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Email already exists. Please use a different email.')
                    return redirect('register')
                
                # Create user with just username and email
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email
                )
                user.save()
                messages.success(request, 'Your profile has been set up! Login and explore your dashboard.')
                return redirect('login')  
                
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                return redirect('register')
        else:
            messages.error(request, 'Password mismatch. Ensure both fields are identical')
            return redirect('register')
    
    return render(request, 'accounts/register.html', context={})

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
            return redirect('app:home')
        else:
            messages.error(
                request,
                'Invalid login credentials'
            )    
    return render(request, 'accounts/login.html', context={})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('app:home')
    