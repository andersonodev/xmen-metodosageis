from rest_framework import serializers
from .models import Task, Column, TaskComment, TaskAttachment


class ColumnSerializer(serializers.ModelSerializer):
    """Serializer para Columns"""
    tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Column
        fields = [
            'id', 'name', 'position', 'board', 'color',
            'created_at', 'updated_at', 'tasks_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'tasks_count']
    
    def get_tasks_count(self, obj):
        return obj.tasks.count()


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Serializer para Task Attachments"""
    
    class Meta:
        model = TaskAttachment
        fields = [
            'id', 'task', 'file', 'file_name', 'file_size',
            'uploaded_by', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_at', 'file_size', 'file_name']


class TaskCommentSerializer(serializers.ModelSerializer):
    """Serializer para Task Comments"""
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskComment
        fields = [
            'id', 'task', 'author', 'author_name', 'content',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'author_name']
    
    def get_author_name(self, obj):
        return obj.author.get_full_name()


class TaskSerializer(serializers.ModelSerializer):
    """Serializer para Tasks"""
    assignee_name = serializers.SerializerMethodField()
    column_name = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assignee', 'assignee_name',
            'column', 'column_name', 'position', 'priority', 'status',
            'due_date', 'estimated_hours', 'actual_hours', 'story_points',
            'created_at', 'updated_at', 'comments_count', 'attachments_count'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'assignee_name', 'column_name',
            'comments_count', 'attachments_count'
        ]
    
    def get_assignee_name(self, obj):
        return obj.assignee.get_full_name() if obj.assignee else None
    
    def get_column_name(self, obj):
        return obj.column.name
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_attachments_count(self, obj):
        return obj.attachments.count()


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para Tasks"""
    assignee = serializers.StringRelatedField()
    column = ColumnSerializer(read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assignee', 'column',
            'position', 'priority', 'status', 'due_date',
            'estimated_hours', 'actual_hours', 'story_points',
            'created_at', 'updated_at', 'comments', 'attachments'
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de tasks"""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assignee', 'column',
            'priority', 'due_date', 'estimated_hours', 'story_points'
        ]
    
    def create(self, validated_data):
        # Define a posição como a última da coluna
        column = validated_data['column']
        last_position = Task.objects.filter(column=column).count()
        validated_data['position'] = last_position
        return super().create(validated_data)


class TaskMoveSerializer(serializers.Serializer):
    """Serializer para mover tasks"""
    column_id = serializers.IntegerField()
    position = serializers.IntegerField(min_value=0)
    
    def validate_column_id(self, value):
        try:
            Column.objects.get(id=value)
        except Column.DoesNotExist:
            raise serializers.ValidationError("Coluna não encontrada")
        return value


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de tasks"""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'assignee', 'priority',
            'status', 'due_date', 'estimated_hours', 'actual_hours',
            'story_points'
        ]


class ColumnCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de colunas"""
    
    class Meta:
        model = Column
        fields = ['name', 'board', 'color']
    
    def create(self, validated_data):
        # Define a posição como a última do board
        board = validated_data['board']
        last_position = Column.objects.filter(board=board).count()
        validated_data['position'] = last_position
        return super().create(validated_data)