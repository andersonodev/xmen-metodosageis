from rest_framework import serializers
from .models import Team, TeamMembership, TeamInvitation


class TeamSerializer(serializers.ModelSerializer):
    """Serializer para Teams"""
    members_count = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'members_count', 'member_count', 
            'max_members', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'members_count', 'member_count', 'created_by', 'created_by_name']
    
    def get_members_count(self, obj):
        return obj.memberships.filter(is_active=True).count()
    
    def get_member_count(self, obj):
        return obj.member_count
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class TeamMembershipSerializer(serializers.ModelSerializer):
    """Serializer para TeamMembership"""
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamMembership
        fields = [
            'id', 'team', 'team_name', 'user', 'user_name', 'user_email',
            'role', 'joined_at', 'is_active'
        ]
        read_only_fields = ['joined_at', 'user_name', 'user_email', 'team_name', 'user']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()
    
    def get_user_email(self, obj):
        return obj.user.email
    
    def get_team_name(self, obj):
        return obj.team.name
    
    def get_user(self, obj):
        """Retorna dados completos do usuário"""
        from apps.accounts.serializers import UserSerializer
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'email': obj.user.email,
            'department': getattr(obj.user, 'department', None),
            'position': getattr(obj.user, 'position', None),
        }


class TeamCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de teams"""
    
    class Meta:
        model = Team
        fields = ['name', 'description', 'leader']
    
    def create(self, validated_data):
        team = Team.objects.create(**validated_data)
        # Adiciona o líder como membro do time automaticamente
        TeamMembership.objects.create(
            team=team,
            user=team.leader,
            role='LEADER'
        )
        return team


class TeamInviteSerializer(serializers.Serializer):
    """Serializer para convites de time"""
    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=TeamMembership.ROLE_CHOICES)
    
    def validate_user_id(self, value):
        from apps.accounts.models import User
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado")
        return value


class TeamMemberDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para membros do time"""
    user = serializers.StringRelatedField()
    skills = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamMembership
        fields = [
            'id', 'user', 'role', 'joined_at', 'is_active', 'skills'
        ]
    
    def get_skills(self, obj):
        from apps.skills.serializers import UserSkillSerializer
        user_skills = obj.user.user_skills.filter(is_active=True)[:5]
        return UserSkillSerializer(user_skills, many=True).data


class TeamInvitationSerializer(serializers.ModelSerializer):
    """Serializer para TeamInvitation"""
    team_name = serializers.SerializerMethodField()
    invited_user_name = serializers.SerializerMethodField()
    invited_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamInvitation
        fields = [
            'id', 'team', 'team_name', 'invited_user', 'invited_user_name',
            'invited_by', 'invited_by_name', 'role', 'status',
            'invited_at', 'responded_at', 'message'
        ]
        read_only_fields = ['invited_at', 'responded_at', 'team_name', 'invited_user_name', 'invited_by_name']
    
    def get_team_name(self, obj):
        return obj.team.name
    
    def get_invited_user_name(self, obj):
        return obj.invited_user.get_full_name()
    
    def get_invited_by_name(self, obj):
        return obj.invited_by.get_full_name()