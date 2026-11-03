from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Client(models.Model):
    """Получатель рассылки (клиент)."""

    email = models.EmailField(
        unique=True,
        verbose_name='Email',
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name='Ф. И. О.',
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name='Владелец',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class Message(models.Model):
    """Сообщение для рассылки."""

    subject = models.CharField(
        max_length=255,
        verbose_name='Тема письма',
    )
    body = models.TextField(
        verbose_name='Тело письма',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Владелец',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    """Рассылка сообщений клиентам.

    Статус вычисляется динамически через update_status().
    """

    STATUS_CREATED = 'Создана'
    STATUS_STARTED = 'Запущена'
    STATUS_FINISHED = 'Завершена'
    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_STARTED, 'Запущена'),
        (STATUS_FINISHED, 'Завершена'),
    ]

    start_time = models.DateTimeField(
        verbose_name='Дата и время начала',
    )
    end_time = models.DateTimeField(
        verbose_name='Дата и время окончания',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name='Статус',
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Сообщение',
    )
    recipients = models.ManyToManyField(
        Client,
        related_name='mailings',
        verbose_name='Получатели',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Владелец',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Рассылка #{self.pk} — {self.message.subject}'

    def clean(self):
        """Валидация: start_time не в прошлом, start_time < end_time."""
        super().clean()
        now = timezone.now()

        if self.start_time and self.start_time < now:
            raise ValidationError({
                'start_time': 'Дата начала не может быть в прошлом.'
            })

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({
                'end_time': 'Дата окончания должна быть позже даты начала.'
            })

    def update_status(self):
        """Пересчитывает статус и сохраняет, если изменился."""
        now = timezone.now()

        if now < self.start_time:
            new_status = self.STATUS_CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.STATUS_STARTED
        else:
            new_status = self.STATUS_FINISHED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])


class MailingAttempt(models.Model):
    """Попытка отправки рассылки."""

    STATUS_SUCCESS = 'Успешно'
    STATUS_FAILED = 'Не успешно'
    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAILED, 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время попытки',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='Статус',
    )
    server_response = models.TextField(
        blank=True,
        verbose_name='Ответ почтового сервера',
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка',
    )

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']

    def __str__(self):
        return f'{self.mailing} — {self.status}'
