from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import SignUp, ChangePassword


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('todo_app:tasks')
    if request.method == 'POST':
        form = SignUp(request.POST)
        if form.is_valid():
            user = form.save()          # Сохраняем нового пользователя
            login(request, user)        # Выполняем вход
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('todo_app:tasks')
    else:
        form = SignUp()
    return render(request, 'signup.html', {'form': form})


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    # Сам требует входа и сохраняет сессию после смены пароля
    template_name = 'password_change.html'
    form_class = ChangePassword
    success_url = reverse_lazy('todo_app:profile')
    success_message = 'Пароль изменён'
