from django import forms
from django.utils import timezone

from .models import Mailing, Client, Message


class MailingForm(forms.ModelForm):
    """Форма создания/редактирования рассылки."""

    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            }),
            'message': forms.Select(attrs={'class': 'form-select'}),
            'recipients': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        }
        labels = {
            'start_time': 'Дата и время начала',
            'end_time': 'Дата и время окончания',
            'message': 'Сообщение',
            'recipients': 'Получатели',
        }

    def clean_start_time(self):
        """start_time не в прошлом."""
        start_time = self.cleaned_data.get('start_time')
        if start_time and start_time < timezone.now():
            raise forms.ValidationError('Дата начала не может быть в прошлом.')
        return start_time

    def clean(self):
        """start_time < end_time."""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError('Дата окончания должна быть позже даты начала.')

        return cleaned_data


class ClientForm(forms.ModelForm):
    """Форма клиента."""

    class Meta:
        model = Client
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MessageForm(forms.ModelForm):
    """Форма сообщения."""

    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }
