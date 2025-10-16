from django import forms
from .models import Task, Column


class TaskForm(forms.ModelForm):
    """Form para criação e edição de tarefas"""
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'type', 'priority', 'status',
            'project', 'column', 'assignee', 'sprint',
            'story_points', 'estimated_hours', 'due_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título da tarefa'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição da tarefa'
            }),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'column': forms.Select(attrs={'class': 'form-control'}),
            'assignee': forms.Select(attrs={'class': 'form-control'}),
            'sprint': forms.Select(attrs={'class': 'form-control'}),
            'story_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100
            }),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtrar projetos do usuário
            self.fields['project'].queryset = user.projects.all()
            
            # Filtrar colunas baseadas no projeto
            if 'project' in self.data:
                try:
                    project_id = int(self.data.get('project'))
                    self.fields['column'].queryset = Column.objects.filter(project_id=project_id)
                except (ValueError, TypeError):
                    self.fields['column'].queryset = Column.objects.none()
            elif self.instance.pk:
                self.fields['column'].queryset = Column.objects.filter(project=self.instance.project)
            else:
                self.fields['column'].queryset = Column.objects.none()


class ColumnForm(forms.ModelForm):
    """Form para criação e edição de colunas"""
    
    class Meta:
        model = Column
        fields = ['name', 'color', 'wip_limit', 'is_done_column']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da coluna'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'wip_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Limite WIP (opcional)'
            }),
            'is_done_column': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }