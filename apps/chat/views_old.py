from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from drf_spectacular.utils import extend_schema, extend_schema_view
import json

from .models import ChatRoom, ChatMembership, Message
from .serializers import ChatRoomSerializer, MessageSerializer

User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=['ChatRooms'], summary='Listar chatrooms'),
    create=extend_schema(tags=['ChatRooms'], summary='Criar chatroom'),
    retrieve=extend_schema(tags=['ChatRooms'], summary='Detalhes do chatroom'),
    update=extend_schema(tags=['ChatRooms'], summary='Atualizar chatroom'),
    destroy=extend_schema(tags=['ChatRooms'], summary='Excluir chatroom'),
)
class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar chatrooms.
    """
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return ChatRoom.objects.all()
        return self.queryset


@extend_schema_view(
    list=extend_schema(tags=['Messages'], summary='Listar messages'),
    create=extend_schema(tags=['Messages'], summary='Criar message'),
    retrieve=extend_schema(tags=['Messages'], summary='Detalhes do message'),
    update=extend_schema(tags=['Messages'], summary='Atualizar message'),
    destroy=extend_schema(tags=['Messages'], summary='Excluir message'),
)
class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'is_staff') and self.request.user.is_staff:
            return Message.objects.all()
        return self.queryset


# Web Views

@login_required
def chat_rooms(request):
    """Listar todas as salas de chat disponíveis."""
    # Buscar salas ativas - assumindo que o usuário pode acessar salas dos projetos em que participa
    user_projects = request.user.team_memberships.filter(is_active=True).values_list('team__projects', flat=True)
    
    rooms = ChatRoom.objects.filter(
        models.Q(project__in=user_projects) | models.Q(project__created_by=request.user),
        is_active=True
    ).select_related('project').distinct().order_by('-created_at')
    
    # Buscar usuários para criar nova sala
    users = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
    
    context = {
        'rooms': rooms,
        'users': users,
    }
    return render(request, 'chat/rooms.html', context)


@login_required
def chat_room(request, room_id):
    """Acessar uma sala de chat específica."""
    room = get_object_or_404(ChatRoom, pk=room_id, is_active=True)
    
    # Verificar se o usuário tem acesso à sala
    if room.is_private and not room.participants.filter(pk=request.user.pk).exists():
        messages.error(request, 'Você não tem acesso a esta sala de chat.')
        return redirect('chat:rooms')
    
    # Buscar mensagens recentes
    recent_messages = Message.objects.filter(
        chat_room=room, 
        is_active=True
    ).select_related('sender').order_by('-created_at')[:50]
    
    # Reverter ordem para exibir da mais antiga para a mais nova
    recent_messages = list(reversed(recent_messages))
    
    # Buscar todas as salas para a sidebar
    rooms = ChatRoom.objects.filter(
        models.Q(participants=request.user) | models.Q(is_private=False),
        is_active=True
    ).prefetch_related('participants').distinct().order_by('-updated_at')
    
    context = {
        'room': room,
        'rooms': rooms,
        'messages': recent_messages,
        'participants': room.participants.all(),
    }
    return render(request, 'chat/room.html', context)


@login_required
def create_room(request):
    """Criar uma nova sala de chat."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_private = request.POST.get('is_private') == 'on'
        participants_ids = request.POST.getlist('participants')
        
        if name:
            room = ChatRoom.objects.create(
                name=name,
                description=description,
                is_private=is_private,
                created_by=request.user,
                is_active=True
            )
            
            # Adicionar o criador como participante
            room.participants.add(request.user)
            
            # Adicionar outros participantes selecionados
            if participants_ids:
                participants = User.objects.filter(pk__in=participants_ids)
                room.participants.add(*participants)
            
            messages.success(request, 'Sala de chat criada com sucesso!')
            return redirect('chat:room', room_id=room.pk)
        else:
            messages.error(request, 'Nome da sala é obrigatório.')
    
    # Buscar usuários para adicionar como participantes
    users = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
    
    context = {
        'users': users,
    }
    return render(request, 'chat/create_room.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Enviar uma mensagem via AJAX."""
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'success': False, 'message': 'Mensagem não pode estar vazia'}, status=400)
        
        room = get_object_or_404(ChatRoom, pk=room_id, is_active=True)
        
        # Verificar se o usuário tem acesso à sala
        if room.is_private and not room.participants.filter(pk=request.user.pk).exists():
            return JsonResponse({'success': False, 'message': 'Acesso negado'}, status=403)
        
        # Criar mensagem
        message = Message.objects.create(
            chat_room=room,
            sender=request.user,
            content=content,
            is_active=True
        )
        
        # Retornar dados da mensagem criada
        response_data = {
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender': {
                    'id': message.sender.id,
                    'name': message.sender.get_full_name() or message.sender.username,
                    'avatar': message.sender.first_name[:1].upper() if message.sender.first_name else message.sender.username[:1].upper()
                },
                'created_at': message.created_at.strftime('%H:%M'),
                'is_own': True
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@csrf_exempt
@require_http_methods(["GET"])
def get_messages(request, room_id):
    """Buscar mensagens de uma sala via AJAX."""
    try:
        room = get_object_or_404(ChatRoom, pk=room_id, is_active=True)
        
        # Verificar acesso
        if room.is_private and not room.participants.filter(pk=request.user.pk).exists():
            return JsonResponse({'success': False, 'message': 'Acesso negado'}, status=403)
        
        # Buscar mensagens recentes
        messages_qs = Message.objects.filter(
            chat_room=room,
            is_active=True
        ).select_related('sender').order_by('-created_at')[:50]
        
        # Reverter ordem
        messages_qs = list(reversed(messages_qs))
        
        messages_data = []
        for message in messages_qs:
            sender_name = message.sender.first_name or message.sender.username
            sender_initial = message.sender.first_name[:1].upper() if message.sender.first_name else message.sender.username[:1].upper()
            
            messages_data.append({
                'id': message.id,
                'content': message.content,
                'sender_name': sender_name,
                'sender_initial': sender_initial,
                'time': message.created_at.strftime('%H:%M'),
                'is_own': message.sender.id == request.user.id
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

