from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .forms import LoginUp
from .views import signup_view, ChangePasswordView

app_name = "user_auth"

urlpatterns = [
    path("login/", LoginView.as_view(template_name='login.html', authentication_form=LoginUp,
                                     redirect_authenticated_user=True), name="login"),  # авторизация
    path("signup/", signup_view, name="signup"),  # регистрация
    path("logout/", LogoutView.as_view(), name='logout'),  # выход (только POST)
    path("password/", ChangePasswordView.as_view(), name="password_change"),  # смена пароля
]
