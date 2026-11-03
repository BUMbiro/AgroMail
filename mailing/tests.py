from django.test import TestCase
from django.test import Client as DjangoTestClient
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import Group
from django.core import mail

from accounts.models import User
from .models import Client as ClientModel, Message, Mailing, MailingAttempt
from .services import send_mailing


class MailingModelTests(TestCase):
    """Тесты модели рассылки (валидация и статусы)."""

    def setUp(self):
        self.user = User.objects.create_user(email='test@test.ru', password='password123')
        self.msg = Message.objects.create(subject='Тема', body='Текст', owner=self.user)
        self.client_obj = ClientModel.objects.create(email='client@test.ru', full_name='Клиент', owner=self.user)

    def test_start_time_in_past_validation(self):
        """start_time не может быть в прошлом."""
        past_time = timezone.now() - timedelta(hours=1)
        mailing = Mailing(
            start_time=past_time,
            end_time=timezone.now() + timedelta(hours=1),
            message=self.msg,
            owner=self.user,
        )
        with self.assertRaises(Exception):
            mailing.full_clean()

    def test_end_time_before_start_time_validation(self):
        """end_time должен быть позже start_time."""
        mailing = Mailing(
            start_time=timezone.now() + timedelta(hours=2),
            end_time=timezone.now() + timedelta(hours=1),
            message=self.msg,
            owner=self.user,
        )
        with self.assertRaises(Exception):
            mailing.full_clean()

    def test_update_status_method(self):
        """Статус пересчитывается динамически."""
        now = timezone.now()
        mailing = Mailing.objects.create(
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
            message=self.msg,
            owner=self.user,
        )
        self.assertEqual(mailing.status, Mailing.STATUS_CREATED)
        mailing.update_status()
        self.assertEqual(mailing.status, Mailing.STATUS_STARTED)


class MailingSendServiceTests(TestCase):
    """Тесты сервиса отправки."""

    def setUp(self):
        self.user = User.objects.create_user(email='test@test.ru', password='password123')
        self.msg = Message.objects.create(subject='Тема', body='Текст', owner=self.user)
        self.client1 = ClientModel.objects.create(email='c1@test.ru', full_name='Клиент 1', owner=self.user)
        self.client2 = ClientModel.objects.create(email='c2@test.ru', full_name='Клиент 2', owner=self.user)

        now = timezone.now()
        self.mailing = Mailing.objects.create(
            start_time=now - timedelta(hours=1),
            end_time=now + timedelta(hours=1),
            message=self.msg,
            owner=self.user,
        )
        self.mailing.recipients.add(self.client1, self.client2)

    def test_send_mailing_success(self):
        """При успешной отправке создаются успешные попытки (bulk_create)."""
        result = send_mailing(self.mailing.pk)

        self.assertTrue(result['success'])
        self.assertEqual(result['sent'], 2)
        self.assertEqual(result['failed'], 0)

        self.assertEqual(self.mailing.attempts.count(), 2)
        self.assertEqual(self.mailing.attempts.filter(status=MailingAttempt.STATUS_SUCCESS).count(), 2)

    def test_send_mailing_out_of_interval(self):
        """Если сейчас не в интервале — отправка запрещена."""
        now = timezone.now()
        self.mailing.start_time = now + timedelta(hours=2)
        self.mailing.end_time = now + timedelta(hours=3)
        self.mailing.save()

        result = send_mailing(self.mailing.pk)
        self.assertFalse(result['success'])
        self.assertIn('запрещена', result['message'])
        self.assertEqual(self.mailing.attempts.count(), 0)


class MailingPermissionsTests(TestCase):
    """Тесты ограничения доступа (Пользователь vs Менеджер)."""

    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@test.ru', password='password123')
        self.user2 = User.objects.create_user(email='user2@test.ru', password='password123')
        self.manager = User.objects.create_user(email='manager@test.ru', password='password123')

        group, _ = Group.objects.get_or_create(name='Менеджер')
        self.manager.groups.add(group)

        self.client_obj = ClientModel.objects.create(email='c1@test.ru', full_name='Клиент', owner=self.user1)
        self.http = DjangoTestClient()

    def test_user_sees_only_own_clients(self):
        """Обычный пользователь видит только своих клиентов."""
        self.http.login(email='user2@test.ru', password='password123')
        response = self.http.get(reverse('mailing:client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.client_obj, response.context['clients'])

        self.http.login(email='user1@test.ru', password='password123')
        response = self.http.get(reverse('mailing:client_list'))
        self.assertIn(self.client_obj, response.context['clients'])

    def test_manager_sees_all_clients(self):
        """Менеджер видит всех клиентов."""
        self.http.login(email='manager@test.ru', password='password123')
        response = self.http.get(reverse('mailing:client_list'))
        self.assertIn(self.client_obj, response.context['clients'])

    def test_user_cannot_edit_others_client(self):
        """Пользователь не может редактировать чужого клиента (404)."""
        self.http.login(email='user2@test.ru', password='password123')
        response = self.http.get(reverse('mailing:client_update', args=[self.client_obj.pk]))
        self.assertEqual(response.status_code, 404)


class AuthTests(TestCase):
    """Тесты регистрации и аутентификации."""

    def setUp(self):
        self.http = DjangoTestClient()

    def test_register_user_and_email_sent(self):
        """Регистрация создает неактивного юзера и отправляет письмо."""
        response = self.http.post(reverse('accounts:register'), {
            'email': 'new@test.ru',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email='new@test.ru')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_email_verified)
        self.assertEqual(len(mail.outbox), 1)

    def test_login_unverified_fails(self):
        """Неподтвержденный пользователь не может войти."""
        user = User.objects.create_user(email='unverified@test.ru', password='password123')
        user.is_active = False
        user.save()

        response = self.http.post(reverse('accounts:login'), {
            'username': 'unverified@test.ru',
            'password': 'password123',
        })
        # Пользователь НЕ вошёл (остался на странице входа)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.http.session)
