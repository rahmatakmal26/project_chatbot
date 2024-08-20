from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Absensi, Log

class IndexView(TemplateView):
    template_name = 'index.html'

def loginView(request):
    context = {
        'page_title': 'LOGIN',
    }
    
    if request.method == "POST":
        username_login = request.POST['username']
        password_login = request.POST['password']
        
        user = authenticate(request, username=username_login, password=password_login)

        if user is not None:
            login(request, user)
            Log.objects.create(user=user, ip_address=request.META.get('REMOTE_ADDR'))
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect('/admin/')
            elif user.role == 'karyawan':
                return redirect('checkin')
            else:
                return redirect('index')
        else:
            return redirect('login')
        
    return render(request, 'login.html', context)

@login_required
def index(request):
    context = {
        'page_title': 'Home',
    }
    return render(request, 'index.html', context)

@login_required
def check_in(request):
    if request.method == 'POST':
        
        Absensi.objects.create(user=request.user, action='checkin')
        
        Log.objects.create(user=request.user, ip_address=request.META.get('REMOTE_ADDR'))
        
        return redirect('dashboard')
    
    return render(request, 'checkin.html')

@login_required
def dashboard(request):
    context = {
        'page_title': 'Dashboard',
        'user': request.user,
    }
    return render(request, 'dashboard.html', context)

@login_required
def check_out(request):
    if request.method == 'POST':

        Absensi.objects.create(user=request.user, action='checkout')

        log = Log.objects.filter(user=request.user).last()
        if log and log.logout_time is None:
            log.logout_time = timezone.now()
            log.save()
        
        return redirect('index') 
    
    return render(request, 'checkout.html')

def logoutView(request):
    context = {
        'page_title': 'Logout',
    }

    if request.method == "POST":
        if request.POST.get("logout") == "Submit":
        
            log = Log.objects.filter(user=request.user).last()
            if log and log.logout_time is None:
                log.logout_time = timezone.now()
                log.save()
            
            logout(request)
            return redirect('index')
    
    return render(request, 'logout.html', context)


