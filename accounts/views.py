from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, RedirectView, TemplateView, View, UpdateView
from django.contrib import messages

from .forms import RegisterForm, LoginForm, ProfileForm
from .models import User
from .tokens import email_verification_token


class RegisterView(CreateView):
    """Регистрация: создаём юзера (неактивного), отправляем письмо."""
    model = User
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:email_verification_sent')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.is_email_verified = False
        user.save()

        token = email_verification_token.make_token(user)
        verify_url = self.request.build_absolute_uri(
            reverse('accounts:verify_email', kwargs={'pk': user.pk, 'token': token})
        )

        send_mail(
            subject='Подтвердите email в АгроПочте',
            message=(
                f'Здравствуйте, {user.email}!\n\n'
                f'Подтвердите свой email, перейдя по ссылке:\n'
                f'{verify_url}\n\n'
                f'Если вы не регистрировались — просто проигнорируйте письмо.'
            ),
            from_email='noreply@agromail.local',
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(
            self.request,
            'Регистрация успешна! Проверьте почту (консоль) и подтвердите email.'
        )
        return redirect(self.success_url)


class VerifyEmailView(View):
    """Подтверждение email по токену."""

    def get(self, request, pk, token):
        user = get_object_or_404(User, pk=pk)

        if email_verification_token.check_token(user, token):
            user.is_active = True
            user.is_email_verified = True
            user.save()
            messages.success(request, 'Email подтверждён! Теперь вы можете войти.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Ссылка недействительна или устарела.')
            return redirect('mailing:home')


class EmailVerificationSentView(TemplateView):
    """Страница «Проверьте почту»."""
    template_name = 'accounts/email_verification_sent.html'


class LoginView(BaseLoginView):
    """Вход по email и паролю. Только для подтверждённых."""
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_email_verified:
            messages.error(
                self.request,
                'Email не подтверждён. Проверьте почту (консоль) и перейдите по ссылке.'
            )
            return redirect('accounts:login')
        return super().form_valid(form)


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


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля (включая аватар)."""
    model = User
    form_class = ProfileForm
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлён!')
        return super().form_valid(form)
