from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django import forms

from .models import User


class SignUp(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text="Введите почту")

    class Meta(UserCreationForm.Meta):
        model = User
        # password1 и password2 UserCreationForm добавляет сама
        fields = ("username", 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class LoginUp(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class EditProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Почта',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }


class ChangePassword(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
