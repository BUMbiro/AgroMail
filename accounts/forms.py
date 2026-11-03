from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from PIL import Image

from .models import User


ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 МБ


class RegisterForm(UserCreationForm):
    """Форма регистрации: email + пароль + подтверждение."""

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
        }),
    )

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтверждение пароля',
        })
        self.fields['password1'].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email


class LoginForm(AuthenticationForm):
    """Форма входа: email + пароль."""

    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
        }),
    )


class ProfileForm(forms.ModelForm):
    """Форма редактирования профиля (с валидацией аватара)."""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'avatar',
            'phone_number', 'country', 'region', 'city',
        ]
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'avatar': 'Аватар',
            'phone_number': 'Телефон',
            'country': 'Страна',
            'region': 'Район',
            'city': 'Город',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'avatar': 'Формат JPEG или PNG, размер до 5 МБ.',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот email уже занят другим пользователем.')
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if not avatar:
            return avatar

        if not hasattr(avatar, 'content_type'):
            return avatar

        if avatar.size > MAX_IMAGE_SIZE:
            raise forms.ValidationError(
                f'Размер изображения не должен превышать 5 МБ. '
                f'Ваш файл: {avatar.size / (1024 * 1024):.1f} МБ.'
            )

        try:
            img = Image.open(avatar)
            img_format = img.format
        except Exception:
            raise forms.ValidationError('Не удалось прочитать изображение. Загрузите корректный файл.')

        if img_format not in ALLOWED_IMAGE_FORMATS:
            raise forms.ValidationError(
                f'Недопустимый формат изображения: {img_format}. '
                f'Разрешены только: {", ".join(ALLOWED_IMAGE_FORMATS)}.'
            )

        avatar.seek(0)
        return avatar
