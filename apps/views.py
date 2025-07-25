import os
import json
import nltk
import random
from nltk.tokenize import word_tokenize
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatHistory, Users
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.db import connection
from django.http import HttpResponse
from collections import Counter
from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from collections import OrderedDict
from datetime import timedelta
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.db.models import Q
import re
import ast
from apps.models import ChatbotInteraksi
from fuzzywuzzy import fuzz
import numpy as np
    
def clean_input(user_input, words_to_remove=None):
    if words_to_remove is None:
        words_to_remove = []

    for word in words_to_remove:
        user_input = user_input.replace(word, "")

    user_input = re.sub(r'[^a-zA-Z0-9\s]', '', user_input)

    return user_input.strip().lower()


def load_stopwords(file_path):
    stopwords = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip().lower()
                if word:
                    stopwords.add(word)
        print("File stopword berhasil dimuat.")
    except Exception as e:
        print(f"Kesalahan saat memuat file stopword: {e}")
    return stopwords

stopwords = load_stopwords('src/dataset/normalization/stopword.txt')


def load_normalization(file_path):
    normalization_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    slang = parts[0]
                    normalized = ' '.join(parts[1:])
                    normalization_dict[slang] = normalized
        print("File normalisasi berhasil dimuat.")
    except Exception as e:
        print(f"Kesalahan saat memuat file normalisasi: {e}")
    return normalization_dict

normalization_dict = load_normalization('src/dataset/normalization/normalization.txt')


def normalize_text(tokens, normalization_dict, stopwords=None):
    normalized_tokens = []
    for token in tokens:
        clean_token = re.sub(r'[^a-zA-Z0-9]', '', token).lower()
        if not clean_token:
            continue
        if stopwords and clean_token in stopwords:
            continue
        
        normalized = normalization_dict.get(clean_token, clean_token)
        normalized_split = normalized.split()
        normalized_tokens.extend(normalized_split)
    return normalized_tokens


def normalize_text_sentence(sentence, normalization_dict):
    cleaned_input = sentence.lower().strip()
    tokens = cleaned_input.split()
    normalized_tokens = normalize_text(tokens, normalization_dict)
    return " ".join(normalized_tokens)




class ChatbotAPI(APIView):
    def post(self, request):
        #  input dari frontend
        user_input = request.data.get('user_input')

        if not request.session.get('is_authenticated'):
            return Response({"response": "Pengguna tidak terautentikasi."}, status=401)

        id_user = request.session.get("id_user")
        try:
            user_instance = Users.objects.get(id_user=id_user)
        except Users.DoesNotExist:
            return Response({"response": "User tidak ditemukan di database."}, status=400)

        if not user_input:
            
            return Response({"error": "No input provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
             #  Cleaning
            cleaned_input = clean_input(user_input)
            print(f"Text Asli: {user_input}") 
            
            tokens = cleaned_input.lower().split()
            print(f"Text Cleaning Input: {tokens}") 

            #  Normalisasi
            normalized_tokens = normalize_text(tokens, normalization_dict)
            print(f"Setelah normalisasi: {normalized_tokens}")       


        except Exception as e:
            print(f"Error saat ekstraksi nama dosen: {e}")
            return Response({"response": "Terjadi kesalahan saat memproses permintaan."}, status=500)
        
         # similarity
        bot_response = self.get_response_from_db(normalized_tokens)

         # cr
        ChatHistory.objects.create(user_input=user_input, bot_response=str(bot_response), user=user_instance)

        # Kembalikan response ke frontend
        return Response({"jawaban": bot_response}, status=status.HTTP_200_OK)
    


    def get_response_from_db(self, normalized_tokens):
        normalized_text = " ".join(normalized_tokens).lower()
        questions = ChatbotInteraksi.objects.all()

        best_match = None
        highest_fuzz_score = -1

        for q in questions:
            questions_text = normalize_text_sentence(q.questions, normalization_dict) if q.questions else ""
            
            ratio_fuzz = fuzz.token_set_ratio(normalized_text, questions_text)

            if ratio_fuzz > highest_fuzz_score:
                highest_fuzz_score = ratio_fuzz
                best_match = q

        if best_match and highest_fuzz_score > 70 and len(normalized_text.split()) >= 3:

            response_text = best_match.answers or ""
            print(f"Respons yang dipilih (score={highest_fuzz_score}): {response_text}")

            file_extensions = {
                "images": ['.jpg', '.jpeg', '.png', '.gif'],
                "documents": ['.pdf', '.xls', '.xlsx', '.ppt', '.pptx', '.doc', '.docx']
            }

            file_name = response_text.strip().split()[-1]
            file_path = None
            file_type = None

            if any(file_name.lower().endswith(ext) for ext in file_extensions["images"]):
                file_path = os.path.join(settings.MEDIA_ROOT, 'foto', file_name)
                file_type = 'image'
            elif any(file_name.lower().endswith(ext) for ext in file_extensions["documents"]):
                file_path = os.path.join(settings.MEDIA_ROOT, 'dokumen', file_name)
                file_type = 'document'

            if file_path and os.path.exists(file_path):
                return {"text": response_text, "file": file_name, "type": file_type}
            
            elif file_path:
                print("File tidak ditemukan di path:", file_path)
                return {"text": response_text, "file": None, "type": None}

            return {"text": response_text, "file": None, "type": None}

        suggestions = self.get_prompt_suggestions(normalized_tokens)
        if suggestions:
            suggestion_text = "<br><br>- " + "<br>- ".join(suggestions)
        else:
            suggestion_text = "\n(Tidak ada saran yang tersedia)"

        return {
            "text": f"Maaf, saya belum memiliki jawaban yang tepat untuk pertanyaan Anda. Mungkin maksud Anda:<br>{suggestion_text}",
            "file": None,
            "type": None
        }
   
    
    def get_prompt_suggestions(self, tokens):
        questions = ChatbotInteraksi.objects.all()
        suggestions = []
        seen_prefix = set()

        for q in questions:
            if not q.questions:
                continue

            utterance = q.questions.lower()
            utterance_tokens = word_tokenize(utterance)
            normalized_utterance_tokens = normalize_text(utterance_tokens, normalization_dict, stopwords)
            match_count = sum((Counter(tokens) & Counter(normalized_utterance_tokens)).values())

            if match_count > 0:
                prefix = " ".join(utterance.split()[:3])

                if prefix not in seen_prefix:
                    suggestions.append((utterance, match_count))
                    seen_prefix.add(prefix)

        suggestions = sorted(suggestions, key=lambda x: x[1], reverse=True)[:2]


        return [s[0] for s in suggestions]
    

class ChatbotSuggestionAPI(APIView):
    def post(self, request):
        user_input = request.data.get('user_input', '').lower()
        if not user_input:
            return Response({"suggestions": []}, status=status.HTTP_400_BAD_REQUEST)

        tokens = word_tokenize(user_input)
        normalized_tokens = normalize_text(tokens, normalization_dict, stopwords)

        suggestions = self.get_prompt_suggestions(normalized_tokens)

        return Response({"suggestions": suggestions}, status=status.HTTP_200_OK)

    def get_prompt_suggestions(self, tokens):
        suggestions = []
        questions = ChatbotInteraksi.objects.all()

        for q in questions:
            if not q.questions:
                continue

            utterance = q.questions.lower()
            utterance_tokens = word_tokenize(utterance)
            normalized_utterance_tokens = normalize_text(utterance_tokens, normalization_dict, stopwords)

            match_count = sum((Counter(tokens) & Counter(normalized_utterance_tokens)).values())
            if match_count > 0:
                suggestions.append((utterance, match_count))

        suggestions = sorted(suggestions, key=lambda x: x[1], reverse=True)
        return [s[0] for s in suggestions[:5]]


class ChatbotInteractionView(APIView):
    def get(self, request):
        today = timezone.now().date()  

        date_range = [(today - timedelta(days=i)) for i in range(3, -2, -1)] 

        daily_interactions = ChatHistory.objects.filter(
            created_at__date__in=date_range
        ).annotate(date=TruncDate('created_at')).values('date').annotate(total=Count('id_histori'))

        interaction_dict = {entry['date']: entry['total'] for entry in daily_interactions}

        labels = [d.strftime('%Y-%m-%d') for d in date_range]
        data = [interaction_dict.get(d, 0) for d in date_range]

        return Response({
            "total_interactions": {
                "labels": labels,
                "data": data
            }
        }, status=status.HTTP_200_OK)



class TopQuestionsView(APIView):
    def get(self, request):
        limit = int(request.query_params.get('limit', 5))

        excluded_responses = ['hay', 'hi', 'hai', 'hello', 'hy']
        exclusion_query = Q()
        for word in excluded_responses:
            exclusion_query |= Q(bot_response__iexact=word)

        top_responses = ChatHistory.objects.exclude(
            exclusion_query
        ).values('bot_response').annotate(
            total=Count('bot_response')
        ).order_by('-total')[:limit * 5]

        labels = []
        data = []

        interaksi_mapping = {
            i.answers.strip(): i.questions.strip()
            for i in ChatbotInteraksi.objects.all() if i.answers and i.questions
        }

        for item in top_responses:
            raw_response = item['bot_response']
            total_count = item['total']

            try:
                parsed = ast.literal_eval(raw_response)
                response_text = parsed.get("text", "").strip()
            except Exception:

                response_text = raw_response.strip()

            if response_text == "Maaf, saya belum memiliki jawaban yang tepat untuk pertanyaan Anda." or \
            response_text == "Hallo ada yang ingin saya bantu? tanyakan sekarang tentang Teknologi Informasi !☺️":
                continue


            pertanyaan = interaksi_mapping.get(response_text)

            if pertanyaan:
                labels.append(pertanyaan)
                data.append(total_count)

            if len(labels) >= limit:
                break

        return Response({
            "top_questions": {
                "labels": labels,
                "data": data
            }
        }, status=status.HTTP_200_OK)




def login_view(request):
    return render(request, 'login/login.html')
def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    return render(request, 'login/register.html')

@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def base_view(request):
    return render(request, 'adminku/base.html')

@login_required(login_url='login')
def sidebar_view(request):
    return render(request, 'sidebar.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard_admin_view(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')

    username = request.session.get('username')
    role = request.session.get('role')

    return render(request, 'adminku/dashboard_admin.html', {'username': username, 'role': role})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard_view(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')

    username = request.session.get('username')
    role = request.session.get('role')

    return render(request, 'dashboard.html', {'username': username, 'role': role})

def get_logged_in_user(request):
    if not request.session.get('is_authenticated'):
        return JsonResponse({"error": "User not authenticated"}, status=401)

    username = request.session.get('username')
    
    try:
        user = Users.objects.get(username=username)
        email = user.email
    except Users.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"email": email, "username": username})



def history_view(request):
    return render(request, 'adminku/history.html')

def answer_view_false(request):
    return render(request, 'adminku/answer_false.html')

def intents(request):
    return render(request, 'adminku/intents.html')


def kategori_interaksi(request):
    return render(request, 'adminku/kategori_interaksi.html')

def matakuliah(request):
    return render(request, 'adminku/matakuliah.html')

def dosen(request):
    return render(request, 'adminku/dosen.html')

def pengampu_mk(request):
    return render(request, 'adminku/pengampu_mk.html')

def panduan(request):
    return render(request, 'adminku/panduan.html')

def berita_admin(request):
    return render(request, 'adminku/berita_admin.html')

def user(request):
    return render(request, 'adminku/user.html')

def berita_view(request):
    return render(request, 'berita.html')

def layanan_view(request):
    return render(request, 'layanan.html')

