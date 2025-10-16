from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey


class SkillCategory(models.Model):
    """
    Categoria de habilidades (ex: Técnicas, Comportamentais, Negócio).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'skill_categories'
        verbose_name = 'Categoria de Habilidade'
        verbose_name_plural = 'Categorias de Habilidades'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Skill(models.Model):
    """
    Habilidade/competência que pode ser atribuída aos usuários.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        SkillCategory, 
        on_delete=models.CASCADE,
        related_name='skills'
    )
    
    # Metadados
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'skills'
        verbose_name = 'Habilidade'
        verbose_name_plural = 'Habilidades'
        ordering = ['category__name', 'name']
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class UserSkill(models.Model):
    """
    Relacionamento entre usuário e habilidade com nível de proficiência.
    """
    LEVEL_CHOICES = [
        (1, 'Iniciante'),
        (2, 'Básico'),
        (3, 'Intermediário'),
        (4, 'Avançado'),
        (5, 'Especialista'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_skills'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='user_skills'
    )
    level = models.IntegerField(
        choices=LEVEL_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Validação/certificação
    is_validated = models.BooleanField(default=False)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_skills'
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_skills'
        verbose_name = 'Habilidade do Usuário'
        verbose_name_plural = 'Habilidades dos Usuários'
        unique_together = ['user', 'skill']
        ordering = ['-level', 'skill__name']
    
    def __str__(self):
        return f"{self.user.username} - {self.skill.name} (Nível {self.level})"
    
    @property
    def level_display(self):
        return self.get_level_display()


class SkillRequirement(models.Model):
    """
    Requisito de habilidade para projetos/times.
    """
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    min_level = models.IntegerField(
        choices=UserSkill.LEVEL_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_mandatory = models.BooleanField(default=True)
    
    # Relacionamento genérico (pode ser usado por Project, Team, etc.)
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'skill_requirements'
        verbose_name = 'Requisito de Habilidade'
        verbose_name_plural = 'Requisitos de Habilidades'
        unique_together = ['skill', 'content_type', 'object_id']
    
    def __str__(self):
        return f"{self.skill.name} (min. nível {self.min_level})"
