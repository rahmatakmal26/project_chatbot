from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import json

class ChatHistoryView(View):
    @csrf_exempt
    def get(self, request, chat_id=None):
        if request.GET.get("all") == "true":
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM chatbot_histori ORDER BY created_at DESC")
                chatbot_histori = cursor.fetchall()

            history_data = [
                {
                    'chat_id': row[0],
                    'user_input': row[2],
                    'message': row[3],
                    'created_at': row[4],
                    'user': row[1],
                }
                for row in chatbot_histori
            ]

            return JsonResponse({
                'chatbot_histori': history_data,
            })
        
        page = int(request.GET.get('page', 1)) 
        per_page = int(request.GET.get('per_page', 10))

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM chatbot_histori")
            total_count = cursor.fetchone()[0]

            total_pages = (total_count // per_page) + (1 if total_count % per_page > 0 else 0)

            cursor.execute(f"SELECT * FROM chatbot_histori ORDER BY created_at DESC LIMIT {per_page} OFFSET {(page - 1) * per_page}")
            chatbot_histori = cursor.fetchall()

        history_data = [
            {
                'chat_id': row[0],
                'user_input': row[2],
                'message': row[3],
                'created_at': row[4],
                'user': row[1],
            }
            for row in chatbot_histori
        ]

        return JsonResponse({
            'chatbot_histori': history_data,
            'page_info': {
                'current_page': page,
                'num_pages': total_pages,
            }
        })


    @csrf_exempt
    def post(self, request):
        """Create a new chat history entry."""
        data = json.loads(request.body)
        message = data.get('message')

        if not message:
            return JsonResponse({'status': 'error', 'message': 'Message is required'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO chatbot_histori (message, created_at) VALUES (%s, NOW())", [message])

        return JsonResponse({'status': 'success', 'message': 'Chat history created'}, status=201)

    @csrf_exempt
    def put(self, request, chat_id):
        """Update a chat history entry."""
        data = json.loads(request.body)
        message = data.get('message')

        if not message:
            return JsonResponse({'status': 'error', 'message': 'Message is required'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("UPDATE chatbot_histori SET message = %s WHERE id_histori= %s", [message, chat_id])

        return JsonResponse({'status': 'success', 'message': 'Chat history updated'}, status=200)


    @csrf_exempt
    def delete(self, request, chat_id):
     if request.method == "DELETE":
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM chatbot_histori WHERE id_histori = %s", [chat_id])
            return JsonResponse({'status': 'success', 'message': 'Chat history dihapus'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
     