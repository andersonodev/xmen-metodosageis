from django import forms
from .models import Project, Sprint


class ProjectForm(forms.ModelForm):
    """Form para criação e edição de projetos"""
    
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'status', 'priority',
            'start_date', 'end_date', 'budget'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do projeto'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição do projeto'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'Orçamento (opcional)'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError('A data de término deve ser posterior à data de início.')

        return cleaned_data


class SprintForm(forms.ModelForm):
    """Form para criação e edição de sprints"""
    
    class Meta:
        model = Sprint
        fields = ['name', 'goal', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do sprint'
            }),
            'goal': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Objetivo do sprint'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError('A data de término deve ser posterior à data de início.')

        return cleaned_data