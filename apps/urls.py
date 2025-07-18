from django.urls import path
from .views import ChatbotAPI, ChatbotSuggestionAPI, ChatbotInteractionView, TopQuestionsView, dashboard_view, layanan_view, login_view, base_view, dashboard_admin_view, sidebar_view, history_view, answer_view_false, intents, kategori_interaksi, register_view, logout_view, dosen, matakuliah, panduan, user, berita_admin, pengampu_mk
from .Chatbot import ChatHistoryView
from .Data import DataMatkulView, DataDosenView, DataPengampuView, DataBeritaView, DataUserView, DataIntentView, DataFilePanduanView, insert_chat_intent, delete_chat_intent, form_pengampu_view, edit_chat_intent
from . import views
from .Controllers import CreateDataUser, UserLoginView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('apps/', ChatbotAPI.as_view(), name='chatbot_api'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('layanan/', layanan_view, name='layanan'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),

    path('adminku/base/', base_view, name='base'),
    path('dashboard_admin/', dashboard_admin_view, name='dashboard_admin'),
    path('sidebar/', sidebar_view, name='sidebar'),
    path('history/', history_view, name='history'),
    path('answer-false/', answer_view_false, name='answer_false'),
    path('intents/', intents, name='intents'),
    path('kategori_interaksi/', kategori_interaksi, name='kategori_interaksi'),
    path('mata-kuliah/', matakuliah, name='matakuliah'),
    path('dosen/', dosen, name='dosen'),
    path('pengampu-mk/', pengampu_mk, name='pengampu_mk'),
    path('panduan/', panduan, name='panduan'),
    path('berita_admin/', berita_admin, name='berita_admin'),

    path('berita/', views.berita_view, name='berita'),

    path('data_intent/', DataIntentView.as_view(), name='data-intent'),
    path('kode-mk/', DataIntentView.get_kode_mk, name='kode-mk'),
    path('id-dosen/', DataIntentView.get_nip, name='id-dosen'),
    path('id-panduan/', DataIntentView.get_id_panduan, name='id-panduan'), 
    path('id-pengampu/', DataIntentView.get_id_pengampu, name='id-pengampu'),

    path('insert-chat-intent/', insert_chat_intent, name='insert_chat_intent'),
    path('edit-chat-intent/<int:id>/', edit_chat_intent, name='edit_chat_intent'),
    path('delete-chat-intent/', delete_chat_intent, name='delete_chat_intent'),

    path('mata_kuliah/', DataMatkulView.as_view(), name='mata-kuliah'),
    path('create/', DataMatkulView.as_view(), name='create-mata-kuliah'),
    path('edit-matkul/<str:kode_mk>/', DataMatkulView.as_view(), name='edit-mata-kuliah'),
    path('delete-matkul/<str:kode_mk>/', DataMatkulView.as_view(), name='delete_data'),

    path('data_dosen/', DataDosenView.as_view(), name='data-dosen'),
    path('create_dosen/', DataDosenView.as_view(), name='create-dosen'),
    path('edit-dosen/<str:nip>/', DataDosenView.edit_dosen, name='edit-dosen'),
    path('delete-dosen/<str:nip>/', DataDosenView.as_view(), name='delete_data'),

    path('data_pengampu/', DataPengampuView.as_view(), name='data-pengampu'),
    path('create_pengampu/', DataPengampuView.as_view(), name='create-pengampu'),
    path('edit-pengampu/<int:id>/', DataPengampuView.edit_pengampu, name='edit-pengampu'),
    path('delete-pengampu/<int:id>/', DataPengampuView.as_view(), name='delete_data'),
    path('pengampu_mk/', form_pengampu_view, name='pengampu-mk'),
    # path('dosen-pengampu/', get_pengampu_mk, name='dosen-pengampu'),

    path('berita/', DataBeritaView.as_view(), name='berita'),
    path('data_berita/', DataBeritaView.as_view(), name='data-berita'),
    path('create_berita/', DataBeritaView.as_view(), name='create-berita'),
    path('edit-berita/<int:id>/', DataBeritaView.edit_berita, name='edit-berita'),
    path('delete-berita/<int:id>/', DataBeritaView.as_view(), name='delete_data'),

    path('file_panduan/', DataFilePanduanView.as_view(), name='file-panduan'),
    path('create_file_panduan/', DataFilePanduanView.as_view(), name='create-file-panduan'),
    path('edit-panduan/<int:id>/', DataFilePanduanView.edit_panduan, name='edit-panduan'),
    path('delete-filepanduan/<int:id>/', DataFilePanduanView.as_view(), name='delete_data'),

    path('user/', user, name='user'),
    path('data_user', DataUserView.as_view(), name='data-user'),
    path('create_user/', DataUserView.as_view(), name='create-user'),
    path('edit-user/<int:id>/', DataUserView.as_view(), name='edit-user'),
    path('delete-user/<int:id>/', DataUserView.as_view(), name='delete-user'),

    path('chat_history/', ChatHistoryView.as_view(), name='chat-history'),
    path('delete-chat/<int:chat_id>/', ChatHistoryView.as_view(), name='delete_chat'),
    path('get-email/', views.get_logged_in_user, name='get_email'),
   
    path('get-suggestions/', ChatbotSuggestionAPI.as_view(), name='get_suggestions'),
    

    path('apps/Chatbot/<int:chat_id>/', ChatHistoryView.as_view(), name='chat_history_detail'),
    path('register_data/', CreateDataUser.as_view(), name='register_data'),
    path('user_login/', UserLoginView.as_view(), name='user_login'),

    path('api/interaction-data/', ChatbotInteractionView.as_view(), name='chatbot_interaction_data'),
    path('api/top-questions/', TopQuestionsView.as_view(), name='top-questions'),


   
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)