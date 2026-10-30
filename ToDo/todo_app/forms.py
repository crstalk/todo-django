from django import forms

from .models import Element, Projects, TaskProject


class TaskForm(forms.ModelForm):
    class Meta:
        model = Element
        fields = ['name', 'data_due']
        labels = {'name': "", 'data_due': "Срок"}
        widgets = {
            "data_due": forms.DateInput(attrs={"type": "date"}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ['name']
        labels = {'name' : ""}


class TaskpForm(forms.ModelForm):
    class Meta:
        model = TaskProject
        fields = ["name"]
        labels = {'name':''}