from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'nik_pegawai', 'divisi', 'agama', 'jenis_kelamin', 'alamat')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        token['nik_pegawai'] = user.nik_pegawai
        token['divisi'] = user.divisi
        token['agama'] = user.agama
        token['jenis_kelamin'] = user.jenis_kelamin
        token['alamat'] = user.alamat
        return token
