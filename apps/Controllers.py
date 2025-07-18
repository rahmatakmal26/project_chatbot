from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
import hashlib
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render



def generate_auth_key():
    secret_key = "rahmat123"
    auth_key = hashlib.sha256(f"{secret_key}".encode()).hexdigest()
    return auth_key


@method_decorator(csrf_exempt, name='dispatch')
class CreateDataUser(View):
    def post(self, request):
        auth_key = generate_auth_key()

        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        nama_lengkap = request.POST.get('nama_lengkap', '')  

        if not all([username, password, confirm_password, email]):
            return JsonResponse({'error': 'Please fill in all required fields'}, status=400)

        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)

        hashed_password = make_password(password)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (password, role, username, nama_lengkap, email, created_time, auth_key)
                    VALUES (%s,'user', %s, %s, %s, NOW(), %s)
                    """,
                    [hashed_password, username, nama_lengkap, email, auth_key]
                )


            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('login')

        except Exception as e:
            return JsonResponse({'error': 'Failed to create user: ' + str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(View):
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        auth_key = generate_auth_key()

        with connection.cursor() as cursor:
            cursor.execute("SELECT id_user, password, auth_key, role FROM users WHERE username = %s", [username])
            user = cursor.fetchone()

        if user:
            id_user, stored_password, stored_auth_key, role = user

            if check_password(password, stored_password):
                if stored_auth_key == auth_key:
                    request.session['id_user'] = id_user
                    request.session['username'] = username
                    request.session['role'] = role
                    request.session['is_authenticated'] = True  

                    if role == 'admin':
                        return redirect('dashboard_admin')
                    else:
                        return redirect('dashboard')
                else:
                    messages.error(request, 'Auth key tidak valid')
            else:
                messages.error(request, 'Username atau password salah')
        else:
            messages.error(request, 'Pengguna tidak ditemukan')

        return redirect('login') 
