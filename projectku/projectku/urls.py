from django.urls import path
from django.contrib import admin
from django.urls import path, include
from karyawan.views import loginView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', loginView, name='login'),
    path('api/', include('api.urls')),
    path('karyawan/', include('karyawan.urls')),
]

