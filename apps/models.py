from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField


class Users(models.Model):
    id_user = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    nama_lengkap = models.CharField(max_length=150)
    password = models.CharField(max_length=150)
    email = models.CharField(max_length=250, unique=True)
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('user', 'User')])
    created_time = models.DateTimeField(auto_now_add=True)
    auth_key = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username


class ChatHistory(models.Model):
    id_histori = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        'Users', to_field='id_user', on_delete=models.CASCADE, db_column='id_user')
    
    user_input = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user_input} | Bot: {self.bot_response}"

    class Meta:
        db_table = "chatbot_histori"


class Berita(models.Model):
    id_berita = models.AutoField(primary_key=True)
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField()
    file_berita = models.CharField(max_length=255, null=True, blank=True)  
    created_time = models.DateTimeField(auto_now_add=True) 
    updated_time = models.DateTimeField(null=True, blank=True)  
    user = models.ForeignKey(
        'Users', to_field='id_user', on_delete=models.CASCADE, db_column='id_user')
    
    class Meta:
        db_table = 'berita'
    
    def __str__(self):
        return self.nama


class MataKuliah(models.Model):
    kode_mk = models.CharField(max_length=20, primary_key=True)
    nama_mk = models.CharField(max_length=100)  
    sks = models.PositiveIntegerField()  
    semester = models.PositiveIntegerField() 
    created_time = models.DateTimeField(auto_now_add=True) 

    class Meta:
        db_table = 'mata_kuliah' 

    def __str__(self):
        return f"{self.kode_mk} - {self.nama_mk}"
    
class Dosen(models.Model):
    nip = models.CharField(max_length=18, primary_key=True)
    nama_lengkap = models.CharField(max_length=100) 
    tempat_lahir = models.TextField() 
    no_hp = models.CharField(max_length=15)  
    mata_kuliah = models.ManyToManyField(MataKuliah)
    

    class Meta:
        db_table = 'dosen'
    def __str__(self):
        return f"{self.nip} - {self.nama_lengkap}"
    
    
class PengampuMk(models.Model):
    id_pengampu = models.AutoField(primary_key=True)  
    nip = models.CharField(max_length=18)
    kode_mk = models.CharField(max_length=20)
    nama_dosen = models.CharField(max_length=100)
    nama_mk = models.CharField(max_length=50)
    kelas = models.CharField(max_length=15)

    class Meta:
        db_table = 'pengampu_mk'  
       

    def __str__(self):
        return f"{self.nama_dosen} - {self.nama_mk} ({self.kelas})"
    
    
class ChatbotInteraksi(models.Model):
    id_interaksi = models.AutoField(primary_key=True)
    intent = models.CharField(max_length=255)
    questions = models.TextField(blank=True, null=True)
    answers = models.TextField(blank=True, null=True)
    kode_mk = models.ForeignKey(
        'MataKuliah', to_field='kode_mk', on_delete=models.CASCADE, db_column='kode_mk')
    nip = models.ForeignKey(
        'Dosen', to_field='nip', on_delete=models.CASCADE, db_column='nip')
    id_pengampu = models.ForeignKey(
        'PengampuMk', to_field='id_pengampu', on_delete=models.CASCADE, db_column='id_pengampu')
    

    class Meta:
        db_table = 'chatbot_interaksi'

    def __str__(self):
        return self.intent
    

    
