from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_ratelimit.decorators import ratelimit


def get_rate(group, request):
    if request.user.is_authenticated:
        return '10/m'
    return '5/m'

def home(request):
    return render(request, 'ip_tracking/home.html')

@ratelimit(key='user_or_ip', rate=get_rate, block=True)
def my_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(user=user, request=request)
            messages.success(request, 'You are logged in')
            return redirect('home')
    return render(request, 'ip_tracking/login.html')

def my_logout(request):
    logout(request)
    return render(request, 'ip_tracking/logout.html')

@login_required(login_url='login')
def profile(request):
    return render(request, 'ip_tracking/profile.html')