from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели User.

    Создаёт пользователей по email, username генерируется автоматически.
    """

    def _generate_unique_username(self, email):
        """Генерирует уникальный username из email."""
        base = email.split('@')[0][:150] or 'user'
        username = base
        counter = 1

        while self.model.objects.filter(username=username).exists():
            suffix = f'-{counter}'
            username = f'{base[:150 - len(suffix)]}{suffix}'
            counter += 1

        return username

    def create_user(self, email, password=None, **extra_fields):
        """Создаёт обычного пользователя по email."""
        if not email:
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)

        if not extra_fields.get('username'):
            extra_fields['username'] = self._generate_unique_username(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создаёт суперюзера."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_email_verified', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Суперюзер должен иметь is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Суперюзер должен иметь is_superuser=True')

        return self.create_user(email, password, **extra_fields)
