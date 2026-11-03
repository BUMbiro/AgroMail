from django.core.mail import send_mail
from django.utils import timezone

from .models import Mailing, MailingAttempt


def send_mailing(mailing_id):
    """Отправляет рассылку и создаёт попытки через bulk_create.

    Возвращает dict:
    - success (bool)
    - message (str)
    - sent (int)
    - failed (int)
    """
    # 1. Получаем рассылку (с обработкой ошибки)
    try:
        mailing = Mailing.objects.select_related('message').prefetch_related('recipients').get(pk=mailing_id)
    except Mailing.DoesNotExist:
        return {'success': False, 'message': 'Рассылка не найдена.', 'sent': 0, 'failed': 0}

    # 2. Проверяем время
    now = timezone.now()
    if not (mailing.start_time <= now <= mailing.end_time):
        return {
            'success': False,
            'message': 'Отправка запрещена: сейчас не в интервале start_time–end_time.',
            'sent': 0,
            'failed': 0,
        }

    # 3. Проверяем, что есть получатели
    recipients = list(mailing.recipients.all())
    if not recipients:
        return {'success': False, 'message': 'Нет получателей для отправки.', 'sent': 0, 'failed': 0}

    # 4. Готовим письма и попытки
    attempts = []
    sent = 0
    failed = 0

    for recipient in recipients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email='noreply@agromail.local',
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            attempts.append(MailingAttempt(
                mailing=mailing,
                status=MailingAttempt.STATUS_SUCCESS,
                server_response='Письмо отправлено.',
            ))
            sent += 1
        except Exception as e:
            attempts.append(MailingAttempt(
                mailing=mailing,
                status=MailingAttempt.STATUS_FAILED,
                server_response=str(e),
            ))
            failed += 1

    # 5. Сохраняем все попытки ОДНИМ запросом (batch)
    MailingAttempt.objects.bulk_create(attempts)

    return {
        'success': True,
        'message': f'Рассылка отправлена. Успешно: {sent}, ошибок: {failed}.',
        'sent': sent,
        'failed': failed,
    }
