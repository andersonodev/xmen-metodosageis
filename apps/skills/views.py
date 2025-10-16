from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Skill, SkillCategory, UserSkill
from .serializers import SkillSerializer, SkillCategorySerializer, UserSkillSerializer


@extend_schema_view(
    list=extend_schema(tags=['Skills'], summary='Listar categorias de habilidades'),
    create=extend_schema(tags=['Skills'], summary='Criar categoria'),
    retrieve=extend_schema(tags=['Skills'], summary='Detalhes da categoria'),
    update=extend_schema(tags=['Skills'], summary='Atualizar categoria'),
    destroy=extend_schema(tags=['Skills'], summary='Excluir categoria'),
)
class SkillCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar categorias de habilidades.
    """
    queryset = SkillCategory.objects.all()
    serializer_class = SkillCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['Skills'], summary='Listar habilidades'),
    create=extend_schema(tags=['Skills'], summary='Criar habilidade'),
    retrieve=extend_schema(tags=['Skills'], summary='Detalhes da habilidade'),
    update=extend_schema(tags=['Skills'], summary='Atualizar habilidade'),
    destroy=extend_schema(tags=['Skills'], summary='Excluir habilidade'),
)
class SkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar habilidades.
    """
    queryset = Skill.objects.filter(is_active=True)
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset


@extend_schema_view(
    list=extend_schema(tags=['User Skills'], summary='Listar habilidades do usuário'),
    create=extend_schema(tags=['User Skills'], summary='Adicionar habilidade'),
    retrieve=extend_schema(tags=['User Skills'], summary='Detalhes da habilidade'),
    update=extend_schema(tags=['User Skills'], summary='Atualizar nível'),
    destroy=extend_schema(tags=['User Skills'], summary='Remover habilidade'),
)
class UserSkillViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar habilidades dos usuários.
    """
    queryset = UserSkill.objects.all()
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_leader() or self.request.user.is_staff:
            return UserSkill.objects.all()
        return UserSkill.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Se não especificado, usar o usuário logado
        if not serializer.validated_data.get('user'):
            serializer.save(user=self.request.user)
        else:
            serializer.save()
    
    @extend_schema(
        tags=['User Skills'],
        summary='Validar habilidade',
        description='Validar habilidade de um usuário (apenas líderes)'
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def validate_skill(self, request, pk=None):
        """
        Validar habilidade de um usuário (apenas líderes).
        """
        if not request.user.is_leader() and not request.user.is_staff:
            return Response(
                {'error': 'Apenas líderes podem validar habilidades'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_skill = self.get_object()
        user_skill.is_validated = True
        user_skill.validated_by = request.user
        user_skill.validated_at = timezone.now()
        user_skill.save()
        
        return Response({'message': 'Habilidade validada com sucesso'})
    
    @extend_schema(
        tags=['User Skills'],
        summary='Habilidades por usuário',
        description='Buscar habilidades de um usuário específico'
    )
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """
        Buscar habilidades de um usuário específico.
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'Parâmetro user_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_skills = UserSkill.objects.filter(user_id=user_id)
        serializer = self.get_serializer(user_skills, many=True)
        return Response(serializer.data)


# Web Views

@login_required
def skill_list(request):
    """Listar todas as habilidades e categorias."""
    # Get all user skills for statistics
    all_user_skills = UserSkill.objects.select_related('skill', 'user')
    user_skills = all_user_skills.filter(user=request.user)
    
    # Calculate statistics
    total_skills = Skill.objects.filter(is_active=True).count()
    my_skills = user_skills.count()
    team_skills = all_user_skills.values('skill').distinct().count()
    skill_categories = SkillCategory.objects.count()
    
    # Get skills with additional info
    skills = Skill.objects.filter(is_active=True).select_related('category')
    
    # Add user's proficiency and endorsement data to each skill
    for skill in skills:
        user_skill = user_skills.filter(skill=skill).first()
        if user_skill:
            skill.proficiency = user_skill.level * 25  # Convert 1-4 to percentage
            skill.user = request.user
        else:
            skill.proficiency = 0
            skill.user = None
            
        # Mock endorsement count (replace with actual endorsement system)
        skill.endorsement_count = 0
    
    context = {
        'skills': skills,
        'total_skills': total_skills,
        'my_skills': my_skills,
        'team_skills': team_skills,
        'skill_categories': skill_categories,
        'user_skills': user_skills,
    }
    return render(request, 'skills/list.html', context)


@login_required
def skill_detail(request, pk):
    """Detalhes de uma habilidade específica."""
    skill = get_object_or_404(Skill, pk=pk, is_active=True)
    
    # Verificar se o usuário tem esta habilidade
    user_skill = UserSkill.objects.filter(user=request.user, skill=skill).first()
    
    context = {
        'skill': skill,
        'user_skill': user_skill,
    }
    return render(request, 'skills/detail.html', context)


@login_required
def add_skill(request, skill_id):
    """Adicionar uma habilidade ao perfil do usuário."""
    skill = get_object_or_404(Skill, pk=skill_id, is_active=True)
    
    # Verificar se já existe
    user_skill, created = UserSkill.objects.get_or_create(
        user=request.user,
        skill=skill,
        defaults={'level': 1}
    )
    
    if created:
        messages.success(request, f'Habilidade "{skill.name}" adicionada ao seu perfil!')
    else:
        messages.info(request, f'Você já possui a habilidade "{skill.name}".')
    
    return redirect('skills:list')


@login_required
def add_user_skill(request):
    """Adicionar uma habilidade ao perfil do usuário via AJAX."""
    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        level = request.POST.get('level')
        
        try:
            skill = Skill.objects.get(pk=skill_id, is_active=True)
            user_skill, created = UserSkill.objects.get_or_create(
                user=request.user,
                skill=skill,
                defaults={'level': level}
            )
            
            if not created:
                user_skill.level = level
                user_skill.save()
            
            return JsonResponse({'success': True, 'message': 'Habilidade adicionada com sucesso!'})
        except Skill.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Habilidade não encontrada'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


@login_required
def remove_skill(request, skill_id):
    """Remover uma habilidade do perfil do usuário."""
    skill = get_object_or_404(Skill, pk=skill_id, is_active=True)
    
    try:
        user_skill = UserSkill.objects.get(user=request.user, skill=skill)
        user_skill.delete()
        messages.success(request, f'Habilidade "{skill.name}" removida do seu perfil!')
    except UserSkill.DoesNotExist:
        messages.error(request, 'Habilidade não encontrada no seu perfil.')
    
    return redirect('skills:list')


@login_required
def update_skill_level(request, skill_id):
    """Atualizar o nível de uma habilidade do usuário."""
    if request.method == 'POST':
        skill = get_object_or_404(Skill, pk=skill_id, is_active=True)
        level = request.POST.get('level')
        
        try:
            user_skill = UserSkill.objects.get(user=request.user, skill=skill)
            user_skill.level = level
            user_skill.save()
            messages.success(request, f'Nível da habilidade "{skill.name}" atualizado!')
        except UserSkill.DoesNotExist:
            messages.error(request, 'Habilidade não encontrada no seu perfil.')
    
    return redirect('skills:list')


@login_required
def skill_create(request):
    """
    View temporária para criar skills - redireciona para a lista por enquanto.
    """
    messages.info(request, 'Funcionalidade em desenvolvimento. Use o botão "Adicionar Skill" na lista.')
    return redirect('skills:list')
