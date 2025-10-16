from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
import json

from .models import ChatRoom, ChatMembership, Message

User = get_user_model()


@login_required
def chat_home(request):
    """Página inicial do chat com salas gerais e de times."""
    
    # Salas que o usuário pode acessar
    user_rooms = ChatRoom.objects.filter(
        members=request.user,
        is_active=True
    ).order_by('-updated_at')
    
    # Sala geral (criar se não existir)
    general_room, created = ChatRoom.objects.get_or_create(
        name='Geral',
        room_type='general',
        defaults={
            'description': 'Conversa geral da plataforma',
            'created_by': request.user,  # Usuário atual
            'is_public': True
        }
    )
    
    # Adicionar usuário à sala geral se não for membro
    if not general_room.members.filter(id=request.user.id).exists():
        ChatMembership.objects.get_or_create(
            room=general_room,
            user=request.user
        )
    
    # Salas de times do usuário
    from apps.teams.models import Team
    user_teams = Team.objects.filter(
        memberships__user=request.user,
        is_active=True
    ).distinct()
    
    # Criar salas para times que não têm
    for team in user_teams:
        team_room, created = ChatRoom.objects.get_or_create(
            name=f'Time: {team.name}',
            room_type='team',
            content_type_id=ContentType.objects.get_for_model(team).id,
            object_id=team.id,
            defaults={
                'description': f'Chat do time {team.name}',
                'created_by': team.created_by,
                'is_public': False
            }
        )
        
        # Adicionar membros do time ao chat
        if created:
            team_members = team.memberships.filter(is_active=True).values_list('user_id', flat=True)
            for member_id in team_members:
                ChatMembership.objects.get_or_create(
                    room=team_room,
                    user_id=member_id
                )
    
    # Atualizar lista de salas
    user_rooms = ChatRoom.objects.filter(
        members=request.user,
        is_active=True
    ).select_related('content_type').order_by('-updated_at')
    
    # Estatísticas para o dashboard
    total_members = User.objects.filter(is_active=True).count()
    messages_today = Message.objects.filter(
        created_at__date=timezone.now().date()
    ).count()
    
    context = {
        'rooms': user_rooms,
        'current_room': general_room,
        'messages': general_room.messages.select_related('sender').order_by('-created_at')[:50][::-1],
        'total_members': total_members,
        'messages_today': messages_today,
    }
    
    return render(request, 'chat/index.html', context)


@login_required
def chat_room(request, room_id):
    """Entrar em uma sala de chat específica."""
    
    room = get_object_or_404(ChatRoom, id=room_id, is_active=True)
    
    # Verificar se o usuário é membro da sala
    if not room.members.filter(id=request.user.id).exists():
        messages.error(request, 'Você não tem acesso a esta sala.')
        return redirect('chat:home')
    
    # Atualizar último acesso
    membership = ChatMembership.objects.get(room=room, user=request.user)
    membership.last_read_at = timezone.now()
    membership.save()
    
    # Buscar mensagens recentes
    recent_messages = room.messages.select_related('sender').order_by('-created_at')[:50]
    recent_messages = list(reversed(recent_messages))
    
    # Buscar todas as salas do usuário para sidebar
    user_rooms = ChatRoom.objects.filter(
        members=request.user,
        is_active=True
    ).select_related('content_type').order_by('-updated_at')
    
    context = {
        'rooms': user_rooms,
        'current_room': room,
        'messages': recent_messages
    }
    
    return render(request, 'chat/index.html', context)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Enviar mensagem via AJAX."""
    
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'success': False, 'error': 'Mensagem vazia'})
        
        room = get_object_or_404(ChatRoom, id=room_id, is_active=True)
        
        # Verificar se é membro
        if not room.members.filter(id=request.user.id).exists():
            return JsonResponse({'success': False, 'error': 'Acesso negado'})
        
        # Criar mensagem
        message = Message.objects.create(
            room=room,
            sender=request.user,
            content=content
        )
        
        # Atualizar timestamp da sala
        room.updated_at = timezone.now()
        room.save()
        
        # Retornar dados da mensagem
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender_name': message.sender.get_full_name() or message.sender.username,
                'sender_avatar': (message.sender.first_name or message.sender.username)[0].upper(),
                'timestamp': message.created_at.strftime('%H:%M'),
                'is_own': True
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_messages(request, room_id):
    """Buscar mensagens via AJAX."""
    
    try:
        room = get_object_or_404(ChatRoom, id=room_id, is_active=True)
        
        # Verificar acesso
        if not room.members.filter(id=request.user.id).exists():
            return JsonResponse({'success': False, 'error': 'Acesso negado'})
        
        # Buscar mensagens
        messages_qs = room.messages.select_related('sender').order_by('-created_at')[:50]
        messages_qs = list(reversed(messages_qs))
        
        messages_data = []
        for msg in messages_qs:
            messages_data.append({
                'id': msg.id,
                'content': msg.content,
                'sender_name': msg.sender.get_full_name() or msg.sender.username,
                'sender_avatar': (msg.sender.first_name or msg.sender.username)[0].upper(),
                'timestamp': msg.created_at.strftime('%H:%M'),
                'is_own': msg.sender.id == request.user.id
            })
        
        return JsonResponse({
            'success': True, 
            'messages': messages_data,
            'room_info': {
                'name': room.name,
                'description': room.description,
                'type': room.room_type
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_direct_chat(request):
    """Criar chat direto com outro usuário."""
    
    try:
        data = json.loads(request.body)
        other_user_id = data.get('user_id')
        
        other_user = get_object_or_404(User, id=other_user_id)
        
        # Verificar se já existe chat direto
        existing_rooms = ChatRoom.objects.filter(
            room_type='direct',
            members=request.user
        ).filter(members=other_user)
        
        if existing_rooms.exists():
            room = existing_rooms.first()
        else:
            # Criar nova sala
            with transaction.atomic():
                room = ChatRoom.objects.create(
                    name=f'{request.user.get_full_name()} & {other_user.get_full_name()}',
                    room_type='direct',
                    description=f'Conversa direta entre {request.user.username} e {other_user.username}',
                    created_by=request.user,
                    is_public=False
                )
                
                # Adicionar membros
                ChatMembership.objects.create(room=room, user=request.user)
                ChatMembership.objects.create(room=room, user=other_user)
        
        return JsonResponse({
            'success': True,
            'room_id': room.id,
            'room_name': room.name
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})