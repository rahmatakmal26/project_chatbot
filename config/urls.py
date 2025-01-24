from django.contrib import admin
from django.urls import include, path
from apps.views import login_view, register_view



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.urls')),
    path('', login_view, name='login'),
    path('', register_view, name='login'),
 
]
