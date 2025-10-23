from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, extend_schema_view

from .forms import TeamCompositionDraftForm
from .models import Team, TeamCompositionDraft, TeamInvitation, TeamMembership
from .serializers import TeamInvitationSerializer, TeamMembershipSerializer, TeamSerializer
from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer


@extend_schema_view(
    list=extend_schema(tags=['Teams'], summary='Listar times'),
    create=extend_schema(tags=['Teams'], summary='Criar time'),
    retrieve=extend_schema(tags=['Teams'], summary='Detalhes do time'),
    update=extend_schema(tags=['Teams'], summary='Atualizar time'),
    destroy=extend_schema(tags=['Teams'], summary='Excluir time'),
)
class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar times.
    """
    queryset = Team.objects.filter(is_active=True)
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Por enquanto, permitir que usuários autenticados vejam todos os times
        if self.request.user.is_staff:
            return Team.objects.all()
        return Team.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        # Extrair dados dos membros antes da validação
        members_data = request.data.pop('members', []) if isinstance(request.data, dict) else []
        
        # Criar o time
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        team = serializer.save(created_by=request.user)
        
        # Adicionar o criador como líder
        TeamMembership.objects.create(
            team=team,
            user=request.user,
            role='product_owner',
            is_active=True,
            is_lead=True,
            joined_at=timezone.now()
        )
        
        # Adicionar membros iniciais se fornecidos
        for member_data in members_data:
            if member_data.get('user_id') != request.user.id:  # Evitar duplicação
                TeamMembership.objects.create(
                    team=team,
                    user_id=member_data.get('user_id'),
                    role=member_data.get('role', 'developer'),
                    is_active=True,
                    joined_at=timezone.now()
                )
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Adicionar membro ao time"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'developer')
        
        # Verificar se já é membro
        if TeamMembership.objects.filter(team=team, user_id=user_id, is_active=True).exists():
            return Response({'error': 'Usuário já é membro do time'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar limite de membros
        if team.member_count >= team.max_members:
            return Response({'error': 'Time já atingiu o limite máximo de membros'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        membership = TeamMembership.objects.create(
            team=team,
            user_id=user_id,
            role=role,
            is_active=True,
            joined_at=timezone.now()
        )
        
        return Response(TeamMembershipSerializer(membership).data)

    @action(detail=True, methods=['get'])
    def available_users(self, request, pk=None):
        """Listar usuários disponíveis para adicionar ao time"""
        team = self.get_object()
        
        # Usuários que não são membros ativos do time
        current_members = TeamMembership.objects.filter(
            team=team, 
            is_active=True
        ).values_list('user_id', flat=True)
        
        available_users = User.objects.exclude(
            id__in=current_members
        ).filter(is_active=True)
        
        serializer = UserSerializer(available_users, many=True)
        return Response({'available_users': serializer.data})

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remover membro do time"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            membership = TeamMembership.objects.get(
                team=team, 
                user_id=user_id, 
                is_active=True
            )
            membership.is_active = False
            membership.left_at = timezone.now()
            membership.save()
            
            return Response({'message': 'Membro removido com sucesso'})
        except TeamMembership.DoesNotExist:
            return Response({'error': 'Membro não encontrado'}, 
                          status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def update_member_role(self, request, pk=None):
        """Atualizar papel de um membro"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')
        
        try:
            membership = TeamMembership.objects.get(
                team=team, 
                user_id=user_id, 
                is_active=True
            )
            membership.role = new_role
            membership.save()
            
            return Response(TeamMembershipSerializer(membership).data)
        except TeamMembership.DoesNotExist:
            return Response({'error': 'Membro não encontrado'}, 
                          status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Listar membros do time"""
        team = self.get_object()
        memberships = TeamMembership.objects.filter(team=team, is_active=True)
        serializer = TeamMembershipSerializer(memberships, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=['Team Memberships'], summary='Listar membros de times'),
    create=extend_schema(tags=['Team Memberships'], summary='Criar membro'),
    retrieve=extend_schema(tags=['Team Memberships'], summary='Detalhes do membro'),
    update=extend_schema(tags=['Team Memberships'], summary='Atualizar membro'),
    destroy=extend_schema(tags=['Team Memberships'], summary='Remover membro'),
)
class TeamMembershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar membros de times.
    """
    queryset = TeamMembership.objects.filter(is_active=True)
    serializer_class = TeamMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        team_id = self.request.query_params.get('team', None)
        if team_id:
            return self.queryset.filter(team_id=team_id)
        return self.queryset


@extend_schema_view(
    list=extend_schema(tags=['Team Invitations'], summary='Listar convites de times'),
    create=extend_schema(tags=['Team Invitations'], summary='Criar convite'),
    retrieve=extend_schema(tags=['Team Invitations'], summary='Detalhes do convite'),
    update=extend_schema(tags=['Team Invitations'], summary='Atualizar convite'),
    destroy=extend_schema(tags=['Team Invitations'], summary='Cancelar convite'),
)
class TeamInvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar convites de times.
    """
    queryset = TeamInvitation.objects.all()
    serializer_class = TeamInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Mostrar convites enviados ou recebidos pelo usuário
        return self.queryset.filter(
            models.Q(team__created_by=self.request.user) |
            models.Q(invited_user=self.request.user)
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Aceitar convite"""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response({'error': 'Convite não está pendente'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Criar membership
        TeamMembership.objects.create(
            team=invitation.team,
            user=invitation.invited_user,
            role=invitation.proposed_role,
            is_active=True,
            joined_at=timezone.now()
        )
        
        # Atualizar convite
        invitation.status = 'accepted'
        invitation.responded_at = timezone.now()
        invitation.save()
        
        return Response({'message': 'Convite aceito com sucesso'})

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Recusar convite"""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response({'error': 'Convite não está pendente'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        invitation.status = 'declined'
        invitation.responded_at = timezone.now()
        invitation.save()
        
        return Response({'message': 'Convite recusado'})


# API Views adicionais

class UserListAPIView(generics.ListAPIView):
    """API para listar todos os usuários disponíveis."""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class JoinTeamAPIView(APIView):
    """API para entrar em um time."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = get_object_or_404(Team, pk=team_id, is_active=True)
            
            # Verificar se já é membro
            if TeamMembership.objects.filter(team=team, user=request.user, is_active=True).exists():
                return Response({'error': 'Usuário já é membro do time'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar limite de membros
            if team.member_count >= team.max_members:
                return Response({'error': 'Time já atingiu o limite máximo de membros'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Criar membership
            TeamMembership.objects.create(
                team=team,
                user=request.user,
                role='developer',
                is_active=True,
                joined_at=timezone.now()
            )
            
            return Response({'message': 'Entrada no time realizada com sucesso'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LeaveTeamAPIView(APIView):
    """API para sair de um time."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = get_object_or_404(Team, pk=team_id, is_active=True)
            membership = get_object_or_404(TeamMembership, team=team, user=request.user, is_active=True)
            
            # Desativar membership
            membership.is_active = False
            membership.left_at = timezone.now()
            membership.save()
            
            return Response({'message': 'Saída do time realizada com sucesso'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AcceptInvitationAPIView(APIView):
    """API para aceitar convite de time."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, invitation_id):
        try:
            invitation = get_object_or_404(TeamInvitation, pk=invitation_id)
            
            if invitation.invited_user != request.user:
                return Response({'error': 'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)
            
            if invitation.status != 'pending':
                return Response({'error': 'Convite não está pendente'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Aceitar convite e criar membership
            invitation.status = 'accepted'
            invitation.responded_at = timezone.now()
            invitation.save()
            
            TeamMembership.objects.create(
                team=invitation.team,
                user=invitation.invited_user,
                role=invitation.proposed_role,
                is_active=True,
                joined_at=timezone.now()
            )
            
            return Response({'message': 'Convite aceito com sucesso'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DeclineInvitationAPIView(APIView):
    """API para recusar convite de time."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, invitation_id):
        try:
            invitation = get_object_or_404(TeamInvitation, pk=invitation_id)
            
            if invitation.invited_user != request.user:
                return Response({'error': 'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)
            
            if invitation.status != 'pending':
                return Response({'error': 'Convite não está pendente'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Recusar convite
            invitation.status = 'declined'
            invitation.responded_at = timezone.now()
            invitation.save()
            
            return Response({'message': 'Convite recusado'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Web Views

@login_required
def team_list(request):
    """Listar todos os times."""
    teams = Team.objects.filter(is_active=True).prefetch_related(
        'memberships', 
        'memberships__user'
    ).select_related('created_by')
    
    # Calculate statistics
    total_teams = teams.count()
    total_members = TeamMembership.objects.filter(is_active=True).values('user').distinct().count()
    active_teams = teams.filter(is_active=True).count()
    total_projects = 0  # Will implement when projects are linked to teams
    
    # Add calculated fields to teams
    for team in teams:
        # Get active members
        active_memberships = team.memberships.filter(is_active=True)
        team.members_list = [m.user for m in active_memberships]
        
        # Get user's role in this team
        user_membership = active_memberships.filter(user=request.user).first()
        team.user_role = user_membership.role if user_membership else None
        team.user_is_leader = user_membership.is_lead if user_membership else False
        
        # Mock project and task counts (replace with actual queries when needed)
        team.project_count = 0  # Count of projects assigned to this team
        team.task_count = 0     # Count of tasks assigned to team members
        
        # Get recent projects (mock for now)
        team.recent_projects = []  # Recent projects for this team
    
    context = {
        'teams': teams,
        'total_teams': total_teams,
        'total_members': total_members,
        'total_projects': total_projects,
        'active_teams': active_teams,
    }
    return render(request, 'teams/list.html', context)


@login_required
def draft_list(request):
    drafts = (
        TeamCompositionDraft.objects.filter(owner=request.user)
        .select_related('project')
        .order_by('-updated_at')
    )

    return render(request, 'teams/drafts.html', {'drafts': drafts})


@login_required
def draft_edit(request, pk=None):
    draft = get_object_or_404(TeamCompositionDraft, pk=pk, owner=request.user) if pk else None
    form = TeamCompositionDraftForm(owner=request.user, data=request.POST or None, instance=draft)

    if request.method == 'POST' and form.is_valid():
        draft = form.save()
        messages.success(request, 'Rascunho de composição salvo com sucesso!')
        if 'save_and_finish' in request.POST:
            draft.is_submitted = True
            draft.save(update_fields=['is_submitted'])
            messages.info(request, 'Rascunho marcado como finalizado. Não esqueça de criar o time oficial.')
        return redirect('teams:draft_list')

    selected_members = []
    if draft:
        selected_members = User.objects.filter(id__in=draft.selected_member_ids())

    context = {
        'form': form,
        'draft': draft,
        'selected_members': selected_members,
    }
    return render(request, 'teams/draft_form.html', context)


@login_required
def team_detail(request, pk):
    """Detalhes de um time específico."""
    team = get_object_or_404(Team, pk=pk)
    
    # Get team members with their roles
    memberships = TeamMembership.objects.filter(
        team=team, 
        is_active=True
    ).select_related('user').order_by('-is_lead', 'role', 'joined_at')
    
    # Get user's membership in this team
    user_membership = memberships.filter(user=request.user).first()
    
    # Get team statistics
    total_members = memberships.count()
    roles_distribution = {}
    for membership in memberships:
        role = membership.get_role_display()
        roles_distribution[role] = roles_distribution.get(role, 0) + 1
    
    context = {
        'team': team,
        'memberships': memberships,
        'user_membership': user_membership,
        'total_members': total_members,
        'roles_distribution': roles_distribution,
        'can_edit': user_membership and user_membership.is_lead or team.created_by == request.user,
    }
    return render(request, 'teams/detail.html', context)


@login_required
def team_create(request):
    """Criar um novo time."""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        max_members = request.POST.get('max_members', 8)
        
        if name:
            team = Team.objects.create(
                name=name,
                description=description,
                max_members=int(max_members),
                created_by=request.user,
                is_active=True
            )
            
            # Adicionar o criador como líder
            TeamMembership.objects.create(
                team=team,
                user=request.user,
                role='product_owner',
                is_active=True,
                is_lead=True,
                joined_at=timezone.now()
            )
            
            messages.success(request, 'Time criado com sucesso!')
            return redirect('teams:detail', pk=team.pk)
        else:
            messages.error(request, 'Nome do time é obrigatório.')
    
    return render(request, 'teams/create.html')


@login_required
def team_edit(request, pk):
    """Editar um time existente."""
    team = get_object_or_404(Team, pk=pk)
    
    # Verificar permissões
    user_membership = TeamMembership.objects.filter(
        team=team, 
        user=request.user, 
        is_active=True
    ).first()
    
    if not (user_membership and user_membership.is_lead) and team.created_by != request.user:
        messages.error(request, 'Você não tem permissão para editar este time.')
        return redirect('teams:detail', pk=team.pk)
    
    if request.method == 'POST':
        team.name = request.POST.get('name', team.name)
        team.description = request.POST.get('description', team.description)
        team.max_members = int(request.POST.get('max_members', team.max_members))
        team.save()
        
        messages.success(request, 'Time atualizado com sucesso!')
        return redirect('teams:detail', pk=team.pk)
    
    context = {
        'team': team,
    }
    return render(request, 'teams/create.html', context)


@login_required
def ajax_team_members(request, pk):
    """API AJAX para listar membros do time."""
    team = get_object_or_404(Team, pk=pk)
    memberships = TeamMembership.objects.filter(
        team=team, 
        is_active=True
    ).select_related('user')
    
    members_data = []
    for membership in memberships:
        user = membership.user
        members_data.append({
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'role': membership.role,
            'role_display': membership.get_role_display(),
            'is_lead': membership.is_lead,
            'joined_at': membership.joined_at.strftime('%d/%m/%Y'),
            'avatar_url': user.avatar.url if user.avatar else None,
        })
    
    return JsonResponse({'members': members_data})

