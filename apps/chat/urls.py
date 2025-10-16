from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Web views
    path('', views.chat_home, name='home'),
    path('room/<int:room_id>/', views.chat_room, name='room'),
    
    # AJAX endpoints
    path('send-message/', views.send_message, name='send_message'),
    path('get-messages/<int:room_id>/', views.get_messages, name='get_messages'),
    path('create-direct/', views.create_direct_chat, name='create_direct'),
]