
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['id', 'task_description', 'task_status', 'task_creation_date']