from rest_framework import serializers
from .models import MetricSnapshot, DashboardWidget, ProjectReport


class MetricSnapshotSerializer(serializers.ModelSerializer):
    """Serializer para MetricSnapshot"""
    project_name = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MetricSnapshot
        fields = [
            'id', 'project', 'project_name', 'team_name', 'date',
            'velocity', 'burndown_remaining', 'lead_time_avg',
            'cycle_time_avg', 'throughput', 'work_in_progress',
            'defect_rate', 'team_satisfaction', 'created_at'
        ]
        read_only_fields = ['created_at', 'project_name', 'team_name']
    
    def get_project_name(self, obj):
        return obj.project.name
    
    def get_team_name(self, obj):
        return obj.project.team.name if obj.project.team else None


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer para DashboardWidget"""
    project_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'project', 'project_name', 'widget_type',
            'title', 'description', 'config', 'position_x',
            'position_y', 'width', 'height', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'project_name']
    
    def get_project_name(self, obj):
        return obj.project.name


class ProjectReportSerializer(serializers.ModelSerializer):
    """Serializer para ProjectReport"""
    project_name = serializers.SerializerMethodField()
    generated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectReport
        fields = [
            'id', 'project', 'project_name', 'report_type', 'title',
            'content', 'parameters', 'generated_at', 'generated_by',
            'generated_by_name', 'file_url', 'is_public'
        ]
        read_only_fields = ['generated_at', 'project_name', 'generated_by_name']
    
    def get_project_name(self, obj):
        return obj.project.name
    
    def get_generated_by_name(self, obj):
        return obj.generated_by.get_full_name() if obj.generated_by else None


class ProjectMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de projeto"""
    project_id = serializers.IntegerField()
    project_name = serializers.CharField()
    team_name = serializers.CharField()
    
    # Métricas atuais
    current_velocity = serializers.FloatField()
    current_burndown = serializers.FloatField()
    current_lead_time = serializers.FloatField()
    current_cycle_time = serializers.FloatField()
    current_throughput = serializers.IntegerField()
    current_wip = serializers.IntegerField()
    
    # Tendências
    velocity_trend = serializers.ListField(child=serializers.FloatField())
    burndown_trend = serializers.ListField(child=serializers.FloatField())
    throughput_trend = serializers.ListField(child=serializers.IntegerField())
    
    # Status geral
    overall_health = serializers.CharField()
    risk_level = serializers.CharField()


class TeamMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de equipe"""
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()
    
    # Métricas da equipe
    avg_velocity = serializers.FloatField()
    avg_lead_time = serializers.FloatField()
    avg_cycle_time = serializers.FloatField()
    total_throughput = serializers.IntegerField()
    satisfaction_score = serializers.FloatField()
    
    # Projetos ativos
    active_projects = serializers.IntegerField()
    
    # Membros
    total_members = serializers.IntegerField()
    skill_distribution = serializers.DictField()


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer para resumo do dashboard"""
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    total_teams = serializers.IntegerField()
    total_users = serializers.IntegerField()
    
    # Métricas globais
    global_velocity = serializers.FloatField()
    global_satisfaction = serializers.FloatField()
    
    # Alertas
    overdue_tasks = serializers.IntegerField()
    at_risk_projects = serializers.IntegerField()
    
    # Últimas atualizações
    last_updated = serializers.DateTimeField()


class WidgetConfigSerializer(serializers.Serializer):
    """Serializer para configuração de widgets"""
    chart_type = serializers.ChoiceField(
        choices=['line', 'bar', 'pie', 'gauge', 'number'],
        required=False
    )
    time_period = serializers.ChoiceField(
        choices=['7d', '30d', '90d', '1y'],
        default='30d'
    )
    metric_type = serializers.ChoiceField(
        choices=['velocity', 'burndown', 'lead_time', 'cycle_time', 'throughput'],
        required=False
    )
    show_trend = serializers.BooleanField(default=True)
    color_scheme = serializers.CharField(max_length=50, required=False)


class MetricsFilterSerializer(serializers.Serializer):
    """Serializer para filtros de métricas"""
    project_id = serializers.IntegerField(required=False)
    team_id = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    metric_types = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "Data de início deve ser anterior à data de fim"
                )
        return data