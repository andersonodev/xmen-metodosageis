from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class ProjectTemplate(models.Model):
    """
    Template para criação rápida de projetos.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    default_duration_days = models.PositiveIntegerField(default=30)
    
    # Skills recomendadas para o template
    recommended_skills = models.ManyToManyField(
        'skills.Skill',
        blank=True,
        through='ProjectTemplateSkill'
    )
    
    # Configurações padrão
    default_team_size = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_templates'
        verbose_name = 'Template de Projeto'
        verbose_name_plural = 'Templates de Projetos'
    
    def __str__(self):
        return self.name


class ProjectTemplateSkill(models.Model):
    """
    Skills recomendadas para um template de projeto.
    """
    template = models.ForeignKey(ProjectTemplate, on_delete=models.CASCADE)
    skill = models.ForeignKey('skills.Skill', on_delete=models.CASCADE)
    min_level = models.IntegerField(default=3)
    is_mandatory = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'project_template_skills'
        unique_together = ['template', 'skill']


class Project(models.Model):
    """
    Projeto que será desenvolvido por um time.
    """
    STATUS_CHOICES = [
        ('planning', 'Planejamento'),
        ('active', 'Ativo'),
        ('on_hold', 'Pausado'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Baixa'),
        (2, 'Normal'),
        (3, 'Alta'),
        (4, 'Crítica'),
    ]
    
    # Informações básicas
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    
    # Relacionamentos
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    template = models.ForeignKey(
        ProjectTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Datas
    start_date = models.DateField()
    end_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Estimativas
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    actual_hours = models.PositiveIntegerField(default=0)
    
    # Metadados
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def is_overdue(self):
        if self.status in ['completed', 'cancelled']:
            return False
        return timezone.now().date() > self.end_date
    
    @property
    def progress_percentage(self):
        if not hasattr(self, '_progress_cache'):
            total_tasks = self.tasks.count()
            if total_tasks == 0:
                self._progress_cache = 0
            else:
                completed_tasks = self.tasks.filter(status='done').count()
                self._progress_cache = int((completed_tasks / total_tasks) * 100)
        return self._progress_cache


class Sprint(models.Model):
    """
    Sprint dentro de um projeto.
    """
    STATUS_CHOICES = [
        ('planning', 'Planejamento'),
        ('active', 'Ativo'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='sprints'
    )
    name = models.CharField(max_length=100)
    goal = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    # Datas
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Métricas
    planned_points = models.PositiveIntegerField(default=0)
    completed_points = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sprints'
        verbose_name = 'Sprint'
        verbose_name_plural = 'Sprints'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class OKR(models.Model):
    """
    Objectives and Key Results para projetos.
    """
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='okrs'
    )
    objective = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Período
    quarter = models.CharField(max_length=10)  # ex: "2024-Q1"
    year = models.PositiveIntegerField()
    
    # Progresso
    progress_percentage = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'okrs'
        verbose_name = 'OKR'
        verbose_name_plural = 'OKRs'
        unique_together = ['project', 'quarter', 'year']
    
    def __str__(self):
        return f"{self.project.name} - {self.objective}"


class KeyResult(models.Model):
    """
    Resultado-chave de um OKR.
    """
    okr = models.ForeignKey(
        OKR,
        on_delete=models.CASCADE,
        related_name='key_results'
    )
    description = models.CharField(max_length=200)
    target_value = models.FloatField()
    current_value = models.FloatField(default=0)
    unit = models.CharField(max_length=50, default='%')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'key_results'
        verbose_name = 'Resultado-Chave'
        verbose_name_plural = 'Resultados-Chave'
    
    def __str__(self):
        return self.description
    
    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(100, int((self.current_value / self.target_value) * 100))
