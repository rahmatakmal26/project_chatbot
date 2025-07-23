from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json
from datetime import datetime
import os
from django.conf import settings
from .utils import save_to_json_file,  delete_from_json_file
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Users, Berita
from django.shortcuts import render, redirect
from django.utils.text import slugify
import re
from .models import ChatbotInteraksi, Dosen 
from django.contrib.auth.hashers import make_password, check_password
import hashlib


def generate_auth_key():
    secret_key = "rahmat123"
    auth_key = hashlib.sha256(f"{secret_key}".encode()).hexdigest()
    return auth_key


class DataUserView(View):
    @csrf_exempt
    def get(self, request, id=None):
        if id is None: 
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM public.users")
                data_user = cursor.fetchall()
            
            user_data = [
                {   
                    'id': row[0], 
                    'username': row[1],
                    'email': row[4],
                    'role': row[5],
                    'nama_lengkap': row[2],
                    'created_time': row[6],
                    'updated_time': row[7]
                   
                }
                for row in data_user
            ]

            return JsonResponse({'data_user': user_data})
        
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        nama_lengkap = request.POST.get('nama_lengkap')

        auth_key = generate_auth_key()
        hashed_password = make_password(password)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (nama_lengkap, username, password, email, role, created_time, auth_key)
                    VALUES (%s, %s, %s, %s, %s, NOW(), %s)
                    """,
                    [nama_lengkap, username, hashed_password, email, role, auth_key]
                )
                
            return JsonResponse({'status': 'success', 'message': 'Data User created'}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
    
    def put(self, request, id):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role = data.get('role')
            nama_lengkap = data.get('nama_lengkap')

            fields = []
            values = []

            if nama_lengkap:
                fields.append("nama_lengkap = %s")
                values.append(nama_lengkap)
            if username:
                fields.append("username = %s")
                values.append(username)
            if email:
                fields.append("email = %s")
                values.append(email)
            if role:
                fields.append("role = %s")
                values.append(role)
            if password:
                hashed_password = make_password(password)
                fields.append("password = %s")
                values.append(hashed_password)

            if not fields:
                return JsonResponse({'status': 'error', 'message': 'No fields to update'}, status=400)

            values.append(id)

            query = f"UPDATE users SET {', '.join(fields)} WHERE id_user = %s"

            with connection.cursor() as cursor:
                cursor.execute(query, values)

            return JsonResponse({'status': 'success', 'message': 'Data User updated'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        

    @csrf_exempt
    def delete(self, request, id):
     if request.method == "DELETE":
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id_user = %s", [id])
            return JsonResponse({'status': 'success', 'message': 'Data Berhasil dihapus'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
        


class DataBeritaView(View):
    @csrf_exempt
    def get(self, request, id=None):
        if id is None:  # Render the HTML template if no id_berita is provided
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM berita order by created_time DESC")
                data_berita = cursor.fetchall()
            
            berita_data = [
                    {   
                        'id': row[0], 
                        'nama': row[1],
                        'deskripsi': row[2],
                        'file_berita': row[3] if row[3] else None,
                        'created_time': row[4].isoformat() if row[4] else None,
                        'updated_time': row[5].isoformat() if row[5] else None,
                        'id_user': row[6]
                    }
                    for row in data_berita
                ]


            return JsonResponse({'data_berita': berita_data})
        return render(request, 'berita.html', {'data_berita': berita_data})
        

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        id_user = request.session.get("id_user")

        user_instance = get_object_or_404(Users, id_user=id_user)

        nama = request.POST.get('nama')
        deskripsi = request.POST.get('deskripsi')
        file_berita = request.FILES.get('file_berita')
        created_time = timezone.now()

        # Validasi input
        if not all([nama, deskripsi, created_time]):
            return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)
        

        berita_file = None
        if file_berita:
                berita_file = f"berita/{file_berita.name}"  
                path = default_storage.save(berita_file, ContentFile(file_berita.read()))

        try:
            with connection.cursor() as cursor:
                Berita.objects.create(
                    nama=nama,
                    deskripsi=deskripsi,
                    file_berita=berita_file,
                    created_time=created_time,
                    user=user_instance
                )

            return JsonResponse({'status': 'success', 'message': 'Data berita created'}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        
    @csrf_exempt
    def edit_berita(request, id): # pakai file (edit berita)
        if request.method == 'POST':
            method = request.POST.get('_method', '').upper()
            if method == 'PUT':
                try:
                    berita_instance = get_object_or_404(Berita, id_berita=id)
                    nama = request.POST.get('nama', berita_instance.nama)
                    deskripsi = request.POST.get('deskripsi', berita_instance.deskripsi)
                    id_user = request.POST.get('id_user', berita_instance.user.id_user)

                    file_berita = request.FILES.get('file_berita')
                    if file_berita:
                        berita_file = f"berita/{file_berita.name}"
                        default_storage.save(berita_file, ContentFile(file_berita.read()))
                        berita_instance.file_berita = berita_file

                    if not all([nama, deskripsi, id_user]):
                        return JsonResponse({'status': 'error', 'message': 'Semua field harus diisi'}, status=400)

                    berita_instance.nama = nama
                    berita_instance.deskripsi = deskripsi
                    berita_instance.id_user = id_user
                    berita_instance.updated_time = timezone.now()
                    berita_instance.save()

                    return JsonResponse({'status': 'success', 'message': 'Data berita berhasil diperbarui'}, status=200)
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            else:
                return JsonResponse({'status': 'error', 'message': 'Method tidak valid'}, status=405)
        else:
            return JsonResponse({'status': 'error', 'message': 'Hanya menerima POST request'}, status=405)

        
    @csrf_exempt
    def delete(self, request, id):
     if request.method == "DELETE":
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM berita WHERE id_berita = %s", [id])
            return JsonResponse({'status': 'success', 'message': 'Data Berhasil dihapus'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


class DataMatkulView(View):
    @csrf_exempt
    def get(self, request, id=None):
        if id is None: 
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM mata_kuliah order by created_time")
                data_mk = cursor.fetchall()
            
            mk_data = [
                {   
                    'kode_mk': row[0],
                    'nama_mk': row[1],
                    'sks': row[3],
                    'semester': row[4],
                    'jenis_mk': row[2],
                    'created_time': row[5],
                    'updated_time': row[6]
                }
                for row in data_mk
            ]

            return JsonResponse({'data_mk': mk_data})
        
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body)
            kode_mk = body.get('kode_mk')
            nama_mk = body.get('nama_mk')
            sks = body.get('sks')
            semester = body.get('semester')
            jenis_mk = body.get('jenis_mk')

            # Validasi input (opsional)
            # if not all([kode_mk, nama_mk, sks, semester, jenis_mk]):
            #     return JsonResponse({'status': 'error', 'message': 'Semua field wajib diisi'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO mata_kuliah (kode_mk, nama_mk, sks, semester, jenis_mk, created_time)
                    VALUES (%s, %s, %s, %s, %s, NOW() )
                    """,
                    [kode_mk, nama_mk, sks, semester, jenis_mk]
                )
            return JsonResponse({'status': 'success', 'message': 'Data mata kuliah berhasil dibuat'}, status=201)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
    @csrf_exempt
    def put(self, request, kode_mk):
        try:
            data = json.loads(request.body)
            kode_mk = data.get('kode_mk')
            nama_mk = data.get('nama_mk')
            sks = data.get('sks')
            semester = data.get('semester')
            jenis_mk = data.get('jenis_mk')

            if not all([kode_mk, nama_mk, sks, semester, jenis_mk]):
                return JsonResponse({'status': 'error', 'message': 'All fields are required'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE mata_kuliah 
                    SET kode_mk = %s, nama_mk = %s, sks = %s, semester = %s, jenis_mk = %s
                    WHERE kode_mk = %s
                    """,
                    [kode_mk, nama_mk, sks, semester, jenis_mk, kode_mk]
                )
            return JsonResponse({'status': 'success', 'message': 'Data mata kuliah updated'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


    
    @csrf_exempt
    def delete(self, request, kode_mk):
     if request.method == "DELETE":
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM mata_kuliah WHERE kode_mk = %s", [kode_mk])
            return JsonResponse({'status': 'success', 'message': 'Data Berhasil dihapus'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
     


     
@csrf_exempt
def get_pengampu_mk(request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT kode_mk, nama_mk FROM mata_kuliah WHERE nama_mk IS NOT NULL")
            pengampu_data = cursor.fetchall()
        
        pengampu_mk_data = [
            {'id': row[0], 'nama_mk': row[1]}
            for row in pengampu_data
        ]
        return JsonResponse(pengampu_mk_data, safe=False)
        
class DataDosenView(View):
    @csrf_exempt
    def get(self, request, id=None):
        if id is None:  # Render the HTML template if no nip is provided
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM dosen order by nip DESC")
                data_dosen = cursor.fetchall()
            
            # Convert the data to a list of dictionaries
            dosen_data = [
                {   
                    'nip':row[0],
                    'nama': row[1],
                    'tempat_lahir': row[2],
                    'no_hp': row[3],
                    'foto': row[4],
                    'created_time': row[5],
                    'updated_time': row[6]
                }
                for row in data_dosen
            ]

            return JsonResponse({'data_dosen': dosen_data})

          
                    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

        try:
            
            nip = request.POST.get('nip')
            nama = request.POST.get('nama')
            tempat_lahir = request.POST.get('tempat_lahir')
            no_hp = request.POST.get('no_hp')
            foto = request.FILES.get('foto')

            foto_filename = None
            if foto:
                nama_slug = slugify(nama)  
                ext = os.path.splitext(foto.name)[1] 
                foto_filename = f"foto/{nama_slug}{ext}" 
                path = default_storage.save(foto_filename, ContentFile(foto.read()))

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO dosen (nip, nama_lengkap, tempat_lahir, no_hp, foto, created_time)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                        """,
                        [nip, nama, tempat_lahir, no_hp, foto_filename]
                    )
            except Exception as db_error:
                return JsonResponse({'status': 'error', 'message': f'Error saving to database: {str(db_error)}'}, status=500)

            return JsonResponse({'status': 'success', 'message': 'Data file panduan created'}, status=201)

        except Exception as general_error:
            return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(general_error)}'}, status=500)
    


    @csrf_exempt
    def edit_dosen(request, nip): # pakai file (edit dosen)
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

        try:
            nama = request.POST.get('nama')
            tempat_lahir = request.POST.get('tempat_lahir')
            no_hp = request.POST.get('no_hp')
            foto = request.FILES.get('foto')

            foto_filename = None
            if foto:
                nama_slug = slugify(nama)
                ext = os.path.splitext(foto.name)[1]
                foto_filename = f"foto/{nama_slug}{ext}"
                path = default_storage.save(foto_filename, ContentFile(foto.read()))

            
            with connection.cursor() as cursor:
                if foto_filename:
                    cursor.execute("""
                        UPDATE dosen SET nama_lengkap=%s, tempat_lahir=%s, no_hp=%s, foto=%s, updated_time=NOW()
                        WHERE nip=%s
                    """, [nama, tempat_lahir, no_hp, foto_filename, nip])
                else:
                    cursor.execute("""
                        UPDATE dosen SET nama_lengkap=%s, tempat_lahir=%s, no_hp=%s, updated_time=NOW()
                        WHERE nip=%s
                    """, [nama, tempat_lahir, no_hp, nip])

            
            dosen = Dosen.objects.get(nip=nip)
            jawaban_interaksi = ChatbotInteraksi.objects.filter(nip=nip)

            for interaksi in jawaban_interaksi:
                # Updt
                if "Tempat Lahir" in interaksi.answers or "tempat lahir" in interaksi.answers:
                    interaksi.answers = f"Tempat Lahir Dosen {dosen.nama_lengkap} di {dosen.tempat_lahir}."
                    interaksi.save()
                
                elif "Nama lengkap" in interaksi.answers or "nama lengkap" in interaksi.answers:
                    interaksi.answers = f"Nama lengkap Dosen tersebut adalah {dosen.nama_lengkap}"
                    interaksi.save()
                
                elif "Foto Dosen" in interaksi.answers or "foto dosen" in interaksi.answers:
                    if dosen.foto:
                        interaksi.answers = f"Foto Dosen {dosen.nama_lengkap} bisa dilihat di /media/{dosen.foto}"
                    else:
                        interaksi.answers = f"Foto Dosen {dosen.nama_lengkap} belum tersedia."
                    interaksi.save()

            return JsonResponse({'status': 'success', 'message': 'Data dosen dan jawaban interaksi updated'}, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    
    @csrf_exempt
    def delete(self, request, nip):
        if request.method == "DELETE":
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM dosen WHERE nip = %s", [nip])
                return JsonResponse({'status': 'success', 'message': 'Data Berhasil dihapus'}, status=200)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)




@csrf_exempt
def form_pengampu_view(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT nip, nama_lengkap FROM dosen")
        dosen_data = cursor.fetchall() 

        cursor.execute("SELECT kode_mk, nama_mk FROM mata_kuliah")
        mk_data = cursor.fetchall()

    daftar_dosen = [{'nip': d[0], 'nama_dosen': d[1]} for d in dosen_data]
    daftar_mk = [{'kode_mk': m[0], 'nama_mk': m[1]} for m in mk_data]

    return JsonResponse({
        'daftar_dosen': daftar_dosen,
        'daftar_mk': daftar_mk
    })



class DataPengampuView(View):
    @csrf_exempt
    def get(self, request, id=None):
        if id is None:  
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM pengampu_mk order by created_time DESC")
                data_pengampu = cursor.fetchall()
            
            # Convert the data to a list of dictionaries
            pengampu_data = [
                {   
                    'id': row[0], 
                    'nip': row[1], 
                    'kode_mk': row[2],
                    'nama_dosen': row[3],
                    'nama_mk': row[4],
                    'kelas': row[5],
                    'created_time': row[6],
                    'updated_time': row[7]
                }
                for row in data_pengampu
            ]

            return JsonResponse({'data_pengampu': pengampu_data})


    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)  
           
            print("Data diterima di edit_pengampu:", data)

            nip = data.get('nip')
            kode_mk = data.get('kode_mk')
            nama_dosen = data.get('nama_dosen') 
            nama_mk = data.get('nama_mk')
            kelas = data.get('kelas')

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM pengampu_mk
                    WHERE nip = %s AND kode_mk = %s AND nama_dosen = %s AND nama_mk = %s AND kelas = %s
                """, [nip, kode_mk, nama_dosen, nama_mk, kelas])
                result = cursor.fetchone()
                if result[0] > 0:
                    return JsonResponse({'status': 'error', 'message': 'Data pengampu sudah ada'}, status=400)

                cursor.execute("""
                    INSERT INTO pengampu_mk (nip, kode_mk, nama_dosen, nama_mk, kelas, created_time)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, [nip, kode_mk, nama_dosen, nama_mk, kelas])

            return JsonResponse({'status': 'success', 'message': 'Data berhasil ditambahkan'}, status=201)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
        
    
    @csrf_exempt
    def edit_pengampu(request, id):
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

        try:
            data = json.loads(request.body)

            nip = data.get('nip')
            kode_mk = data.get('kode_mk')
            nama_dosen = data.get('nama_dosen')
            nama_mk = data.get('nama_mk')
            kelas = data.get('kelas')

            if not all([nip, kode_mk, nama_dosen, nama_mk, kelas]):
                return JsonResponse({'status': 'error', 'message': 'Semua field wajib diisi'}, status=400)

            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM pengampu_mk WHERE id_pengampu = %s", [id])
                exists = cursor.fetchone()[0]

                if exists == 0:
                    return JsonResponse({'status': 'error', 'message': 'Data pengampu tidak ditemukan'}, status=404)

                cursor.execute("""
                    UPDATE pengampu_mk 
                    SET nip = %s, kode_mk = %s, nama_dosen = %s, nama_mk = %s, kelas = %s
                    WHERE id_pengampu = %s
                """, [nip, kode_mk, nama_dosen, nama_mk, kelas, id])

            return JsonResponse({'status': 'success', 'message': 'Data pengampu berhasil diupdate'}, status=200)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        
    @csrf_exempt
    def delete(self, request, id):
        if request.method == "DELETE":
            try:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM pengampu_mk WHERE id_pengampu = %s", [id])
                return JsonResponse({'status': 'success', 'message': 'Data Berhasil dihapus'}, status=200)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
        


class DataFilePanduanView(View):
    @csrf_exempt
    def get(self, request, id=None):
        if id is None:  
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM panduan_akademik order by created_time DESC")
                data_filepanduan = cursor.fetchall()
            
            # Convert the data to a list of dictionaries
            filepanduan_data = [
                {   
                    'id': row[0], 
                    'nama': row[1],
                    'file_panduan': row[2],
                    'created_time': row[3],
                    'updated_time': row[4]
                }
                for row in data_filepanduan
            ]

            return JsonResponse({'data_filepanduan': filepanduan_data})
        
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

        try:
            nama = request.POST.get('nama')
            file_panduan = request.FILES.get('file_panduan')
            tgl = datetime.now()

            if not nama:
                return JsonResponse({'status': 'error', 'message': 'Nama is required'}, status=400)
            # if not deskripsi:
            #     return JsonResponse({'status': 'error', 'message': 'Deskripsi is required'}, status=400)
            if not file_panduan:
                return JsonResponse({'status': 'error', 'message': 'File panduan is required'}, status=400)

            def to_snake_case(text):
        
                clean_text = re.sub(r'[^\w\s-]', '', text)
                return re.sub(r'[\s-]+', '_', clean_text.strip().lower())

            file_extension = os.path.splitext(file_panduan.name)[1].lower()
            new_file_name = f"{to_snake_case(nama)}{file_extension}"

            file_directory = os.path.join(settings.MEDIA_ROOT, 'dokumen')
            os.makedirs(file_directory, exist_ok=True) 

            file_path = os.path.join(file_directory, new_file_name)
            try:
                with open(file_path, 'wb+') as destination:
                    for chunk in file_panduan.chunks():
                        destination.write(chunk)
            except Exception as file_error:
                return JsonResponse({'status': 'error', 'message': f'Error saving file: {str(file_error)}'}, status=500)

            relative_path = f"dokumen/{new_file_name}"

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO panduan_akademik (nama, file_panduan, created_time)
                        VALUES (%s, %s, %s)
                        """,
                        [nama, relative_path, tgl]
                    )
            except Exception as db_error:
                return JsonResponse({'status': 'error', 'message': f'Error saving to database: {str(db_error)}'}, status=500)

            return JsonResponse({'status': 'success', 'message': 'Data file panduan created'}, status=201)

        except Exception as general_error:
            return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(general_error)}'}, status=500)


    @csrf_exempt
    def edit_panduan(request, id):
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Hanya menerima POST request'}, status=405)

        method = request.POST.get('_method', '').upper()
        if method != 'PUT':
            return JsonResponse({'status': 'error', 'message': 'Method tidak valid'}, status=405)

        try:
            nama = request.POST.get('nama')
            file_panduan = request.FILES.get('file_panduan')

            if not nama:
                return JsonResponse({'status': 'error', 'message': 'Nama is required'}, status=400)
            # if not deskripsi:
            #     return JsonResponse({'status': 'error', 'message': 'Deskripsi is required'}, status=400)

            def to_snake_case(text):
                clean_text = re.sub(r'[^\w\s-]', '', text)
                return re.sub(r'[\s-]+', '_', clean_text.strip().lower())

            with connection.cursor() as cursor:
                cursor.execute("SELECT file_panduan FROM panduan_akademik WHERE id_panduan= %s", [id])
                old_file = cursor.fetchone()

            file_directory = os.path.join(settings.MEDIA_ROOT, 'dokumen')
            os.makedirs(file_directory, exist_ok=True)

            if file_panduan:
                file_extension = os.path.splitext(file_panduan.name)[1].lower()
                new_file_name = f"{to_snake_case(nama)}{file_extension}"
                file_path = os.path.join(file_directory, new_file_name)

                try:
                    with open(file_path, 'wb+') as destination:
                        for chunk in file_panduan.chunks():
                            destination.write(chunk)

                    if old_file and old_file[0] and old_file[0] != f"dokumen/{new_file_name}":
                        old_file_path = os.path.join(settings.MEDIA_ROOT, old_file[0])
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                except Exception as file_error:
                    return JsonResponse({'status': 'error', 'message': f'Error saving file: {str(file_error)}'}, status=500)

                final_file_path = f"dokumen/{new_file_name}"
            else:
                final_file_path = old_file[0] if old_file else None

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE panduan_akademik
                        SET nama = %s, file_panduan = %s, updated_time = NOW()
                        WHERE id_panduan= %s
                        """,
                        [nama, final_file_path, id]
                    )
            except Exception as db_error:
                return JsonResponse({'status': 'error', 'message': f'Error updating database: {str(db_error)}'}, status=500)

            return JsonResponse({'status': 'success', 'message': 'Data panduan berhasil diperbarui'}, status=200)
        except Exception as general_error:
            return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(general_error)}'}, status=500)

        
     
    @csrf_exempt
    def delete(self, request, id):
        if request.method == "DELETE":
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT file_panduan FROM panduan_akademik WHERE id_panduan = %s", [id])
                    result = cursor.fetchone()
                    file_path_db = result[0] if result else None

                    cursor.execute("DELETE FROM panduan_akademik WHERE id_panduan= %s", [id])

                #remove
                if file_path_db:
                    full_path = os.path.join(settings.MEDIA_ROOT, file_path_db)
                    if os.path.exists(full_path):
                        os.remove(full_path)

                return JsonResponse({'status': 'success', 'message': 'Data dan file berhasil dihapus'}, status=200)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

     

class DataIntentView(View):
    @csrf_exempt
    def get(self, request, id=None):
        if id is None: 
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM chatbot_interaksi ORDER BY id_interaksi DESC")
                data_intent = cursor.fetchall()
            
            intent_data = [
                {   
                    'id': row[0], 
                    'intent': row[1],
                    'questions': row[3],
                    'answers': row[4],
                    'kode_mk': row[2],
                    'id_panduan': row[5],
                    'nip': row[6],
                    'id_pengampu': row[7]
                }
                for row in data_intent
            ]

            return JsonResponse({'data_intent': intent_data})
        
    @csrf_exempt
    def get_kode_mk(request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT kode_mk, nama_mk, semester, sks, jenis_mk FROM mata_kuliah")
            data = cursor.fetchall()

        kode_mk_list = [{"kode_mk": row[0],
                         "nama_mk": row[1], 
                         "semester": row[2],
                         "sks": row[3],
                         "jenis_mk": row[4]} for row in data]

        return JsonResponse(kode_mk_list, safe=False)
    
    @csrf_exempt
    def get_nip(request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT nip, nama_lengkap, tempat_lahir, no_hp, foto FROM dosen")
            data = cursor.fetchall()

        nip_list = [{"nip": row[0],
                          "nama_dosen": row[1],
                          "tempat_lahir": row[2],
                          "no_hp": row[3],
                          "foto": row[4]} for row in data]

        return JsonResponse(nip_list, safe=False)
    
    @csrf_exempt
    def get_id_pengampu(request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_pengampu, nama_dosen, nama_mk, kelas FROM pengampu_mk")
            data = cursor.fetchall()

        id_pengampu_list = [{"id_pengampu": row[0],
                          "nama_dosen": row[1],
                          "nama_mk": row[2],
                          "kelas": row[3]} for row in data]

        return JsonResponse(id_pengampu_list, safe=False)
    
    @csrf_exempt
    def get_id_panduan(request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_panduan, nama, file_panduan FROM panduan_akademik")
            data = cursor.fetchall()

        id_panduan_list = [{"id_panduan": row[0],
                          "nama_panduan": row[1],
                          "file_panduan": row[2]} for row in data]

        return JsonResponse(id_panduan_list, safe=False)
        



@csrf_exempt
def insert_chat_intent(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            intent = data.get("intent")
            questions = data.get("questions")
            answers = data.get("answers")
            kode_mk = data.get("kode_mk") 
            nip = data.get("nip") 
            id_panduan = data.get("id_panduan") 
            id_pengampu = data.get("id_pengampu")


            if isinstance(questions, str):
                questions = [questions]
            if isinstance(answers, str):
                answers = [answers]

            if len(questions) != len(answers):
                return JsonResponse({"error": "Jumlah questions dan answers harus sama."}, status=400)

            with connection.cursor() as cursor:

                if id_panduan == "all" or id_pengampu == "all" or kode_mk == "all":
                    if id_panduan == "all":
                        cursor.execute("SELECT id_panduan, nama, file_panduan FROM panduan_akademik")
                        all_panduan = cursor.fetchall()
                        if not all_panduan:
                            return JsonResponse({"error": "Tidak ada data panduan ditemukan."}, status=400)

                        for panduan in all_panduan:
                            panduan_id, nama_panduan, file_panduan = panduan
                            pertanyaan = f"File {nama_panduan} yang mana?"
                            jawaban = (
                                f"Berikut file {nama_panduan}: {file_panduan.split('/')[-1]}"
                                if file_panduan else
                                f"File {nama_panduan} belum tersedia."
                            )
                            cursor.execute("""
                                INSERT INTO chatbot_interaksi (intent, questions, answers, id_panduan, created_time)
                                VALUES (%s, %s, %s, %s, NOW()) 
                            """, [intent, pertanyaan, jawaban, panduan_id])

                    if id_pengampu == "all":
                        cursor.execute("SELECT id_pengampu, nama_dosen, nama_mk, kelas FROM pengampu_mk")
                        all_pengampu = cursor.fetchall()
                        if not all_pengampu:
                            return JsonResponse({"error": "Tidak ada data pengampu ditemukan."}, status=400)

                        for pg in all_pengampu:
                            id_pengampu, nama_dosen, nama_mk, kelas = pg
                            pertanyaan = f"Mata kuliah {nama_mk} Kelas {kelas} siapa dosen pengampunya?"
                            jawaban = f"Dosen pengampu mata kuliah {nama_mk} kelas {kelas} adalah {nama_dosen}."
                            cursor.execute("""
                                INSERT INTO chatbot_interaksi (intent, questions, answers, id_pengampu, created_time)
                                VALUES (%s, %s, %s, %s, NOW())
                            """, [intent, pertanyaan, jawaban, id_pengampu])


                    if kode_mk == "all":
                        cursor.execute("SELECT kode_mk, nama_mk, semester, jenis_mk, sks FROM mata_kuliah")
                        all_mk = cursor.fetchall()
                        if not all_mk:
                            return JsonResponse({"error": "Tidak ada data mata kuliah ditemukan."}, status=400)

                        for mk in all_mk:
                            kode, nama, semester, jenis_mk, sks = mk

                            questions = [
                                f"Mata kuliah {nama} berapa kode mk-nya?",
                                f"Mata kuliah {nama} bisa diambil di semester berapa?",
                                f"Mata kuliah {nama} itu termasuk kategori / peminatan apa?",
                                f"Mata kuliah {nama} berapa sks?"
                            ]
                            answers = [
                                f"Kode mata kuliah {nama} adalah {kode or 'belum tersedia'}.",
                                f"Mata kuliah {nama} bisa diambil di semester {semester or 'belum tersedia'}.",
                                f"Mata kuliah {nama} termasuk kategori {jenis_mk or 'belum tersedia'}.",
                                f"{'Informasi SKS tidak tersedia.' if not sks else f'Mata kuliah {nama} memiliki {sks} SKS.'}"
                            ]

                            for q, a in zip(questions, answers):
                                cursor.execute("""
                                    INSERT INTO chatbot_interaksi (intent, questions, answers, kode_mk, created_time)
                                    VALUES (%s, %s, %s, %s, NOW())
                                """, [intent, q, a, kode])


                else:
                    if isinstance(questions, str):
                        questions = [questions]
                    if isinstance(answers, str):
                        answers = [answers]

                    if len(questions) != len(answers):
                        return JsonResponse({"error": "Jumlah questions dan answers harus sama."}, status=400)

                    if kode_mk:
                        cursor.execute("SELECT kode_mk FROM mata_kuliah WHERE kode_mk = %s", [kode_mk])
                        if not cursor.fetchone():
                            return JsonResponse({"error": "Kode MK tidak ditemukan di database."}, status=400)

                    if nip:
                        cursor.execute("SELECT nip FROM dosen WHERE nip = %s", [nip])
                        if not cursor.fetchone():
                            return JsonResponse({"error": "ID dosen tidak ditemukan di database."}, status=400)

                    if id_pengampu:
                        cursor.execute("SELECT id_pengampu FROM pengampu_mk WHERE id_pengampu = %s", [id_pengampu])
                        if not cursor.fetchone():
                            return JsonResponse({"error": "ID pengampu tidak ditemukan di database."}, status=400)

                    for utt, ans in zip(questions, answers):
                        cursor.execute("""
                            INSERT INTO chatbot_interaksi (intent, questions, answers, kode_mk, nip, id_panduan, id_pengampu, created_time)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                        """, [intent, utt, ans, kode_mk, nip, id_panduan, id_pengampu])


            return JsonResponse({"message": "Semua intent berhasil disimpan!"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Format JSON tidak valid."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Metode request tidak valid."}, status=405)


@csrf_exempt
def edit_chat_intent(request, id):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            intent = data.get("intent")
            questions = data.get("questions")
            answers = data.get("answers")
            nip = data.get("nip")
            kode_mk = data.get("kode_mk")
            id_panduan = int(data.get("id_panduan")) if data.get("id_panduan") else None
            id_pengampu = int(data.get("id_pengampu")) if data.get("id_pengampu") else None


            if id_pengampu is not None and not isinstance(id_pengampu, int):
                return JsonResponse({"error": "id_pengampu harus berupa integer."}, status=400)


            if not intent or not questions or not answers:
                return JsonResponse({"error": "Intent, questions, dan answers wajib diisi."}, status=400)

            if isinstance(questions, str):
                questions = [questions]
            if isinstance(answers, str):
                answers = [answers]

            if len(questions) != len(answers):
                return JsonResponse({"error": "Jumlah questions dan answers harus sama."}, status=400)

            with connection.cursor() as cursor:
                if kode_mk:
                    cursor.execute("SELECT kode_mk FROM mata_kuliah WHERE kode_mk = %s", [kode_mk])
                    if not cursor.fetchone():
                        return JsonResponse({"error": "Kode MK tidak ditemukan di database."}, status=400)

                if nip:
                    cursor.execute("SELECT nip FROM dosen WHERE nip = %s", [nip])
                    if not cursor.fetchone():
                        return JsonResponse({"error": "ID dosen tidak ditemukan di database."}, status=400)
                    
                if id_pengampu:
                    cursor.execute("SELECT id_pengampu FROM pengampu_mk WHERE id_pengampu = %s", [id_pengampu])
                    if not cursor.fetchone():
                        return JsonResponse({"error": "Kode MK tidak ditemukan di database."}, status=400)

                cursor.execute("DELETE FROM chatbot_interaksi WHERE id_interaksi = %s", [id])

                for utt, ans in zip(questions, answers):
                    cursor.execute("""
                        INSERT INTO chatbot_interaksi (intent, questions, answers, kode_mk, nip, id_panduan, id_pengampu)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, [intent, utt, ans, kode_mk, nip, id_panduan, id_pengampu])

            return JsonResponse({"message": "Intent berhasil diupdate!"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Format JSON tidak valid."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Metode request tidak valid."}, status=405)




@csrf_exempt
def delete_chat_intent(request):
    if request.method == "POST":
        try:
        
            data = json.loads(request.body)
            intent_id = data.get("id") 

            if not intent_id:
                return JsonResponse(
                    {"error": "ID field is required."},
                    status=400
                )

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT intent FROM chatbot_interaksi WHERE id_interaksi = %s
                    """,
                    [intent_id]
                )
                row = cursor.fetchone()

                if not row:
                    return JsonResponse(
                        {"error": "Intent with the given ID not found in database."},
                        status=404
                    )

                intent_name = row[0]  

                cursor.execute(
                    """
                    DELETE FROM chatbot_interaksi
                    WHERE id_interaksi = %s
                    """,
                    [intent_id]
                )

            print(f"Intent dengan ID {intent_id} berhasil dihapus dari database.")

            try:
                delete_from_json_file(intent_name)  
                print(f"Intent '{intent_name}' berhasil dihapus dari file JSON.")
            except Exception as e:
                print("Error saat menghapus data dari file JSON:", str(e))
                raise e

            return JsonResponse({"message": "Intent deleted successfully!"}, status=200)

        except json.JSONDecodeError as e:
            print("Error JSONDecodeError:", str(e))
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            print("Error tak terduga:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    print("Metode request tidak valid:", request.method)
    return JsonResponse({"error": "Invalid request method."}, status=405)
