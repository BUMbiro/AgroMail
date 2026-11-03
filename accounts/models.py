from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """Кастомная модель пользователя.

    Вход по email (USERNAME_FIELD), username генерируется автоматически.
    Доп. поля: avatar, phone_number, country, is_email_verified.
    """

    email = models.EmailField(
        unique=True,
        verbose_name='Email',
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар',
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон',
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Страна',
    )
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name='Email подтверждён',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Подключаем кастомный менеджер
    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def is_manager(self):
        """Менеджер: состоит в группе «Менеджер»."""
        return self.groups.filter(name='Менеджер').exists()
