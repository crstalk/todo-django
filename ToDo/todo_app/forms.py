from django import forms

from .models import Task, Project


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'date_due']
        labels = {'name': "Задача", 'date_due': "Срок"}
        help_texts = {'date_due': "Необязательно. Задачи на сегодня появятся во вкладке «Сегодня»."}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Что нужно сделать?", "autofocus": True}),
            "date_due": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']
        labels = {'name': "Название проекта"}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например: Ремонт, Учёба, Отпуск", "autofocus": True}),
        }
