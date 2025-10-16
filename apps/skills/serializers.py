from rest_framework import serializers
from .models import Skill, SkillCategory, UserSkill


class SkillCategorySerializer(serializers.ModelSerializer):
    """Serializer para categorias de habilidades."""
    
    skills_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SkillCategory
        fields = ['id', 'name', 'description', 'icon', 'skills_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_skills_count(self, obj):
        return obj.skills.filter(is_active=True).count()


class SkillSerializer(serializers.ModelSerializer):
    """Serializer para habilidades."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'users_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_users_count(self, obj):
        return obj.user_skills.count()


class UserSkillSerializer(serializers.ModelSerializer):
    """Serializer para habilidades dos usuários."""
    
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    validated_by_name = serializers.CharField(source='validated_by.get_full_name', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = [
            'id', 'user', 'user_name', 'skill', 'skill_name', 'skill_category',
            'level', 'level_display', 'is_validated', 'validated_by', 
            'validated_by_name', 'validated_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_validated', 'validated_by', 'validated_at', 'created_at', 'updated_at'
        ]


class UserSkillCreateSerializer(serializers.ModelSerializer):
    """Serializer para criar habilidades de usuário."""
    
    class Meta:
        model = UserSkill
        fields = ['user', 'skill', 'level']
    
    def validate(self, attrs):
        # Verificar se a combinação user+skill já existe
        if UserSkill.objects.filter(
            user=attrs['user'], 
            skill=attrs['skill']
        ).exists():
            raise serializers.ValidationError(
                "Usuário já possui esta habilidade cadastrada."
            )
        return attrs