from django.urls import path
from .views import IndexView, loginView, logoutView
from django.contrib import admin
from . import views

urlpatterns = [
    path('index/', IndexView.as_view(), name='index'),
    path('', loginView, name='login'),
    path('checkin/', views.check_in, name='checkin'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('checkout/', views.check_out, name='checkout'),
    path('logout/', logoutView, name='logout'),
]