import os
import json

def save_to_json_file(intent_data):
    folder_path = 'src/dataset/corpus'
    file_path = os.path.join(folder_path, 'tif.json')

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(intent_data)

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)  # Pastikan encoding tetap benar

    


def delete_from_json_file(intent):
    folder_path = 'src/dataset/corpus'
    file_path = os.path.join(folder_path, 'tif.json')

    # Pastikan file JSON ada
    if not os.path.exists(file_path):
        print(f"File JSON tidak ditemukan: {file_path}")
        raise FileNotFoundError(f"File {file_path} tidak ditemukan.")

    try:
        # Membaca data dari file JSON
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Cek apakah data berbentuk list
        if not isinstance(data, list):
            print("Data di file JSON bukan list.")
            raise ValueError("Data di file JSON tidak valid.")

        # Mencari intent yang akan dihapus
        data = [item for item in data if item.get('intent') != intent]

        # Menyimpan kembali data ke file JSON setelah dihapus
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
            print(f"Data berhasil diperbarui di file JSON.")
    except Exception as e:
        print(f"Terjadi error saat menghapus data dari file JSON: {e}")
        raise e





# from twilio.rest import Client
# from .models import Dosen

# # Fungsi untuk mengirim pesan WhatsApp
# def send_whatsapp_message(no_hp, nama):
#     # SID dan Token Twilio
#     account_sid = 'YOUR_ACCOUNT_SID'
#     auth_token = 'YOUR_AUTH_TOKEN'
#     client = Client(account_sid, auth_token)

#     # Pesan yang dipersonalisasi
#     message_body = f"Salam {nama}, waktu ujian semester 7 tinggal 1 minggu lagi. Tolong belajar dari sekarang."

#     # Kirim pesan melalui WhatsApp
#     message = client.messages.create(
#         from_='whatsapp:+14155238886',  # Nomor resmi WhatsApp Twilio
#         body=message_body,
#         to=f'whatsapp:{no_hp}'  # Nomor tujuan dengan format internasional
#     )

#     # Cek apakah pesan berhasil dikirim
#     print(f"Pesan terkirim ke {nama}: {message.sid}")

# # Fungsi untuk mengambil data pengguna dan mengirim pesan
# def send_messages_to_all_users():
#     users = Dosen.objects.all()  # Mengambil semua pengguna dari database
#     for user in users:
#         send_whatsapp_message(user.no_hp(), user.nama)