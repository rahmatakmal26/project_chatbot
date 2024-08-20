from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    AGAMA_CHOICES = [
        ('Islam', 'Islam'),
        ('Kristen', 'Kristen'),
        ('Katolik', 'Katolik'),
        ('Hindu', 'Hindu'),
        ('Budha', 'Budha'),
        ('Konghucu', 'Konghucu'),
    ]

    JENIS_KELAMIN_CHOICES = [
        ('Laki-laki', 'Laki-laki'),
        ('Perempuan', 'Perempuan'),
    ]

    DIVISI_CHOICES = [
        ('IT', 'IT'),
        ('HRD', 'HRD'),
        ('Finance', 'Finance'),
        ('Marketing', 'Marketing'),
    ]
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('karyawan', 'Karyawan'),
    )
    nik_pegawai = models.CharField(max_length=20, unique=True)
    divisi = models.CharField(max_length=100, choices= DIVISI_CHOICES)
    
    agama = models.CharField(max_length=50, choices= AGAMA_CHOICES)
    jenis_kelamin = models.CharField(max_length=15, choices=JENIS_KELAMIN_CHOICES)
    alamat = models.TextField(max_length=100)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='karyawan'
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nik_pegawai'], name='unique_nik_pegawai')
        ]
    