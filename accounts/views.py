from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, RedirectView, UpdateView, TemplateView
from django.contrib import messages

from .forms import RegisterForm, LoginForm
from .models import User


class RegisterView(CreateView):
    """Регистрация нового пользователя."""
    model = User
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('mailing:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Логиним сразу после регистрации
        login(self.request, self.object)
        messages.success(self.request, 'Регистрация успешна! Добро пожаловать.')
        return response


class LoginView(BaseLoginView):
    """Вход по email и паролю."""
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class LogoutView(RedirectView):
    """Выход из системы."""
    url = reverse_lazy('mailing:home')
    permanent = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, 'Вы вышли из аккаунта.')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Страница профиля пользователя."""
    template_name = 'accounts/profile.html'
