from rest_framework import serializers
from .models import Project, Sprint, OKR, KeyResult


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer para Projects"""
    team_name = serializers.SerializerMethodField()
    sprints_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'team', 'team_name',
            'status', 'start_date', 'end_date', 'created_at',
            'updated_at', 'sprints_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'team_name', 'sprints_count']
    
    def get_team_name(self, obj):
        return obj.team.name if obj.team else None
    
    def get_sprints_count(self, obj):
        return obj.sprints.count()


class SprintSerializer(serializers.ModelSerializer):
    """Serializer para Sprints"""
    project_name = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Sprint
        fields = [
            'id', 'name', 'description', 'project', 'project_name',
            'start_date', 'end_date', 'goal', 'status',
            'created_at', 'updated_at', 'tasks_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'project_name', 'tasks_count']
    
    def get_project_name(self, obj):
        return obj.project.name
    
    def get_tasks_count(self, obj):
        return obj.tasks.count()


class OKRSerializer(serializers.ModelSerializer):
    """Serializer para OKRs"""
    project_name = serializers.SerializerMethodField()
    key_results_count = serializers.SerializerMethodField()
    completion_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = OKR
        fields = [
            'id', 'title', 'description', 'project', 'project_name',
            'quarter', 'year', 'status', 'created_at', 'updated_at',
            'key_results_count', 'completion_percentage'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'project_name', 
            'key_results_count', 'completion_percentage'
        ]
    
    def get_project_name(self, obj):
        return obj.project.name
    
    def get_key_results_count(self, obj):
        return obj.key_results.count()
    
    def get_completion_percentage(self, obj):
        key_results = obj.key_results.all()
        if not key_results:
            return 0
        total_progress = sum(kr.current_value / kr.target_value * 100 
                           for kr in key_results if kr.target_value > 0)
        return round(total_progress / len(key_results), 1) if key_results else 0


class KeyResultSerializer(serializers.ModelSerializer):
    """Serializer para Key Results"""
    okr_title = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = KeyResult
        fields = [
            'id', 'title', 'description', 'okr', 'okr_title',
            'target_value', 'current_value', 'unit', 'status',
            'created_at', 'updated_at', 'progress_percentage'
        ]
        read_only_fields = ['created_at', 'updated_at', 'okr_title', 'progress_percentage']
    
    def get_okr_title(self, obj):
        return obj.okr.title
    
    def get_progress_percentage(self, obj):
        if obj.target_value > 0:
            return round((obj.current_value / obj.target_value) * 100, 1)
        return 0


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de projetos"""
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'team', 'start_date', 'end_date']
    
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "Data de início deve ser anterior à data de fim"
                )
        return data


class SprintCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de sprints"""
    
    class Meta:
        model = Sprint
        fields = ['name', 'description', 'project', 'start_date', 'end_date', 'goal']
    
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "Data de início deve ser anterior à data de fim"
                )
        return data


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para projetos"""
    team = serializers.StringRelatedField()
    sprints = SprintSerializer(many=True, read_only=True)
    okrs = OKRSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'team', 'status',
            'start_date', 'end_date', 'created_at', 'updated_at',
            'sprints', 'okrs'
        ]