import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer para chat em tempo real por projeto.
    """
    
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'chat_{self.project_id}'
        
        # Verificar se o usuário está autenticado
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return
        
        # Verificar se o usuário tem acesso ao projeto
        has_access = await self.check_project_access()
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            message_type = text_data_json.get('type', 'text')
            reply_to = text_data_json.get('reply_to')
            
            # Salvar mensagem no banco
            saved_message = await self.save_message(message, message_type, reply_to)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': saved_message
                }
            )
        except json.JSONDecodeError:
            pass
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'data': event['message']
        }))
    
    @database_sync_to_async
    def check_project_access(self):
        from apps.projects.models import Project
        try:
            project = Project.objects.get(id=self.project_id)
            # Verificar se usuário é membro do time do projeto
            if project.team:
                return project.team.memberships.filter(
                    user=self.scope["user"],
                    is_active=True
                ).exists()
            # Se não tem time, verificar se é o criador
            return project.created_by == self.scope["user"]
        except Project.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content, message_type='text', reply_to=None):
        from apps.chat.models import ChatRoom, Message
        from apps.projects.models import Project
        
        try:
            project = Project.objects.get(id=self.project_id)
            room, created = ChatRoom.objects.get_or_create(
                project=project,
                defaults={'name': f'Chat {project.name}'}
            )
            
            reply_message = None
            if reply_to:
                try:
                    reply_message = Message.objects.get(id=reply_to, room=room)
                except Message.DoesNotExist:
                    pass
            
            message = Message.objects.create(
                room=room,
                sender=self.scope["user"],
                content=content,
                message_type=message_type,
                reply_to=reply_message
            )
            
            return {
                'id': message.id,
                'content': message.content,
                'message_type': message.message_type,
                'sender': {
                    'id': message.sender.id,
                    'username': message.sender.username,
                    'full_name': message.sender.get_full_name()
                },
                'reply_to': reply_to,
                'created_at': message.created_at.isoformat(),
            }
        except Exception:
            return None


class BoardConsumer(AsyncWebsocketConsumer):
    """
    Consumer para atualizações do quadro Kanban em tempo real.
    """
    
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'board_{self.project_id}'
        
        # Verificar autenticação e acesso
        if self.scope["user"] == AnonymousUser():
            await self.close()
            return
        
        has_access = await self.check_project_access()
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            event_type = data.get('type')
            
            if event_type == 'task_moved':
                await self.handle_task_moved(data)
            elif event_type == 'task_updated':
                await self.handle_task_updated(data)
        except json.JSONDecodeError:
            pass
    
    async def handle_task_moved(self, data):
        task_id = data.get('task_id')
        new_column_id = data.get('new_column_id')
        new_position = data.get('new_position')
        
        # Atualizar tarefa no banco
        success = await self.move_task(task_id, new_column_id, new_position)
        
        if success:
            # Notificar outros clientes
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'task_moved',
                    'task_id': task_id,
                    'new_column_id': new_column_id,
                    'new_position': new_position,
                    'moved_by': self.scope["user"].username
                }
            )
    
    async def handle_task_updated(self, data):
        task_id = data.get('task_id')
        updates = data.get('updates', {})
        
        # Atualizar tarefa no banco
        task_data = await self.update_task(task_id, updates)
        
        if task_data:
            # Notificar outros clientes
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'task_updated',
                    'task': task_data,
                    'updated_by': self.scope["user"].username
                }
            )
    
    async def task_moved(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_moved',
            'data': event
        }))
    
    async def task_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_updated',
            'data': event
        }))
    
    @database_sync_to_async
    def check_project_access(self):
        from apps.projects.models import Project
        try:
            project = Project.objects.get(id=self.project_id)
            if project.team:
                return project.team.memberships.filter(
                    user=self.scope["user"],
                    is_active=True
                ).exists()
            return project.created_by == self.scope["user"]
        except Project.DoesNotExist:
            return False
    
    @database_sync_to_async
    def move_task(self, task_id, new_column_id, new_position):
        from apps.tasks.models import Task, Column
        try:
            task = Task.objects.get(id=task_id, project_id=self.project_id)
            new_column = Column.objects.get(id=new_column_id, project_id=self.project_id)
            
            task.column = new_column
            task.position = new_position
            task.save()
            
            # Criar histórico
            from apps.tasks.models import TaskHistory
            TaskHistory.objects.create(
                task=task,
                user=self.scope["user"],
                action='moved',
                details={
                    'from_column': task.column_id,
                    'to_column': new_column_id,
                    'position': new_position
                }
            )
            
            return True
        except (Task.DoesNotExist, Column.DoesNotExist):
            return False
    
    @database_sync_to_async
    def update_task(self, task_id, updates):
        from apps.tasks.models import Task
        try:
            task = Task.objects.get(id=task_id, project_id=self.project_id)
            
            for field, value in updates.items():
                if hasattr(task, field):
                    setattr(task, field, value)
            
            task.save()
            
            return {
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'assignee': task.assignee.username if task.assignee else None,
                'updated_at': task.updated_at.isoformat()
            }
        except Task.DoesNotExist:
            return None