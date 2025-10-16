from django.db import models
from django.conf import settings


class Integration(models.Model):
    """
    Integrações externas configuradas.
    """
    TYPE_CHOICES = [
        ('csv_import', 'Importação CSV'),
        ('trello', 'Trello'),
        ('github', 'GitHub'),
        ('slack', 'Slack'),
        ('jira', 'Jira'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('inactive', 'Inativa'),
        ('error', 'Erro'),
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    
    # Configurações da integração
    config = models.JSONField(default=dict)
    credentials = models.JSONField(default=dict, blank=True)  # criptografado
    
    # Estado
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inactive')
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True, null=True)
    
    # Relacionamentos
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='integrations',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'integrations'
        verbose_name = 'Integração'
        verbose_name_plural = 'Integrações'
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class ImportHistory(models.Model):
    """
    Histórico de importações realizadas.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
    ]
    
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name='import_history'
    )
    
    # Dados da importação
    source_file = models.FileField(upload_to='imports/', null=True, blank=True)
    source_data = models.JSONField(default=dict, blank=True)
    
    # Resultados
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_records = models.PositiveIntegerField(default=0)
    processed_records = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    
    # Logs
    log_data = models.JSONField(default=list, blank=True)
    error_details = models.TextField(blank=True, null=True)
    
    # Metadados
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'import_history'
        verbose_name = 'Histórico de Importação'
        verbose_name_plural = 'Histórico de Importações'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Importação {self.id} - {self.integration.name}"
