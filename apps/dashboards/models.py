from django.db import models
from django.conf import settings


class MetricSnapshot(models.Model):
    """
    Snapshot de métricas de um projeto em um momento específico.
    """
    METRIC_TYPE_CHOICES = [
        ('velocity', 'Velocity'),
        ('burndown', 'Burndown'),
        ('lead_time', 'Lead Time'),
        ('cycle_time', 'Cycle Time'),
        ('throughput', 'Throughput'),
        ('wip', 'Work in Progress'),
    ]
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='metric_snapshots'
    )
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPE_CHOICES)
    
    # Dados da métrica
    value = models.FloatField()
    period = models.CharField(max_length=50)  # ex: "Sprint 1", "2024-01", "Week 5"
    data = models.JSONField(default=dict, blank=True)  # dados detalhados
    
    # Metadados
    calculated_at = models.DateTimeField(auto_now_add=True)
    calculated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'metric_snapshots'
        verbose_name = 'Snapshot de Métrica'
        verbose_name_plural = 'Snapshots de Métricas'
        ordering = ['-calculated_at']
        unique_together = ['project', 'metric_type', 'period']
    
    def __str__(self):
        return f"{self.project.name} - {self.get_metric_type_display()} ({self.period})"


class ProjectReport(models.Model):
    """
    Relatório de projeto gerado automaticamente.
    """
    REPORT_TYPE_CHOICES = [
        ('sprint_summary', 'Resumo do Sprint'),
        ('team_performance', 'Performance do Time'),
        ('project_health', 'Saúde do Projeto'),
        ('risk_analysis', 'Análise de Riscos'),
    ]
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='reports'
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    
    # Conteúdo do relatório
    summary = models.TextField()
    data = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list, blank=True)
    
    # Período do relatório
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Metadados
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'project_reports'
        verbose_name = 'Relatório do Projeto'
        verbose_name_plural = 'Relatórios dos Projetos'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.title}"


class DashboardWidget(models.Model):
    """
    Widget personalizado para dashboard de um usuário.
    """
    WIDGET_TYPE_CHOICES = [
        ('task_summary', 'Resumo de Tarefas'),
        ('team_velocity', 'Velocity do Time'),
        ('project_progress', 'Progresso do Projeto'),
        ('upcoming_deadlines', 'Prazos Próximos'),
        ('team_workload', 'Carga de Trabalho'),
        ('recent_activity', 'Atividade Recente'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_widgets'
    )
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPE_CHOICES)
    title = models.CharField(max_length=100)
    
    # Configuração do widget
    config = models.JSONField(default=dict, blank=True)
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=4)
    height = models.PositiveIntegerField(default=3)
    
    # Estado
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_widgets'
        verbose_name = 'Widget do Dashboard'
        verbose_name_plural = 'Widgets do Dashboard'
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
