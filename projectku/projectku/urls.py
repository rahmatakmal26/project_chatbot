from django.contrib import admin
from django.urls import path
from django.urls import path, include
from .views import WelcomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', WelcomeView.as_view(), name='welcome')
]

