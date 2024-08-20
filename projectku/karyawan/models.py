from django.conf import settings
from django.db import models

class Absensi(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

class Log(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f'Log for {self.user} at {self.login_time}'
    
    """test"""

