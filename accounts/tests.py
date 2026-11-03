from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from accounts.tokens import email_verification_token
from django.contrib.auth import authenticate


class UserManagerTests(TestCase):
    """Тесты кастомного менеджера User."""

    def test_create_user_without_username(self):
        """username генерируется автоматически из email."""
        user = User.objects.create_user(email='test@test.ru', password='pwd')
        self.assertEqual(user.username, 'test')
        self.assertTrue(user.check_password('pwd'))

    def test_create_superuser(self):
        """Суперюзер создается с нужными флагами."""
        admin = User.objects.create_superuser(email='admin@test.ru', password='pwd')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_email_verified)


class EmailVerificationTests(TestCase):
    """Тесты подтверждения email."""

    def setUp(self):
        self.user = User.objects.create_user(email='test@test.ru', password='pwd')
        self.user.is_active = False
        self.user.save()

    def test_verify_email_view(self):
        """Переход по ссылке активирует пользователя."""
        token = email_verification_token.make_token(self.user)
        url = reverse('accounts:verify_email', kwargs={'pk': self.user.pk, 'token': token})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Редирект на логин

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.is_email_verified)
