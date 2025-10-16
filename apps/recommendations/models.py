from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey


class Recommendation(models.Model):
    """
    Recomendações da IA para projetos e times.
    """
    TYPE_CHOICES = [
        ('team_allocation', 'Alocação de Time'),
        ('skill_match', 'Compatibilidade de Skills'),
        ('delay_risk', 'Risco de Atraso'),
        ('role_suggestion', 'Sugestão de Papel'),
        ('workload_balance', 'Balanceamento de Carga'),
    ]
    
    CONFIDENCE_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
    ]
    
    # Relacionamento genérico
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Tipo e conteúdo da recomendação
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Dados da IA
    confidence = models.CharField(max_length=10, choices=CONFIDENCE_CHOICES)
    score = models.FloatField(help_text="Score de 0 a 1")
    data = models.JSONField(default=dict, blank=True)
    
    # Estado
    is_active = models.BooleanField(default=True)
    is_applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applied_recommendations'
    )
    
    # Feedback
    user_feedback = models.CharField(
        max_length=20,
        choices=[
            ('helpful', 'Útil'),
            ('not_helpful', 'Não Útil'),
            ('incorrect', 'Incorreta'),
        ],
        null=True,
        blank=True
    )
    feedback_comment = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendations'
        verbose_name = 'Recomendação'
        verbose_name_plural = 'Recomendações'
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"


class AIModel(models.Model):
    """
    Configuração dos modelos de IA utilizados.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    version = models.CharField(max_length=20)
    
    # Configurações
    config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    
    # Métricas de performance
    accuracy_score = models.FloatField(null=True, blank=True)
    last_trained_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_models'
        verbose_name = 'Modelo de IA'
        verbose_name_plural = 'Modelos de IA'
    
    def __str__(self):
        return f"{self.name} v{self.version}"
