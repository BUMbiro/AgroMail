from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.conf import settings

from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
from .services import send_mailing


class OwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_superuser:
            raise PermissionDenied('У вас нет прав на управление этим объектом.')

        return super().dispatch(request, *args, **kwargs)


# ============================================================
# Главная (с кэшем)
# ============================================================

class HomeView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            if user.is_manager or user.is_superuser:
                cache_key = 'home_stats_manager'
            else:
                cache_key = f'home_stats_user_{user.pk}'
        else:
            cache_key = 'home_stats_anonymous'

        stats = cache.get(cache_key)

        if stats is None:
            if not user.is_authenticated:
                total = Mailing.objects.count()
                active = Mailing.objects.filter(status=Mailing.STATUS_STARTED).count()
                recipients = Client.objects.count()
            elif user.is_manager or user.is_superuser:
                total = Mailing.objects.count()
                active = Mailing.objects.filter(status=Mailing.STATUS_STARTED).count()
                recipients = Client.objects.count()
            else:
                user_mailings = Mailing.objects.filter(owner=user)
                total = user_mailings.count()
                active = user_mailings.filter(status=Mailing.STATUS_STARTED).count()
                recipients = Client.objects.filter(owner=user).count()

            stats = {
                'total_mailings': total,
                'active_mailings': active,
                'unique_recipients': recipients,
            }
            cache.set(cache_key, stats, timeout=settings.CACHE_TTL_HOME)

        context.update(stats)
        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=60'
        return response


# ============================================================
# Клиенты (с кэшем списков и детальных)
# ============================================================

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_manager or user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'mailing/client_detail.html'
    context_object_name = 'client'

    def get_queryset(self):
        user = self.request.user
        if user.is_manager or user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(owner=user)


class ClientCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_message = 'Клиент «%(full_name)s» добавлен!'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mailing:client_detail', kwargs={'pk': self.object.pk})


class ClientUpdateView(LoginRequiredMixin, OwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_message = 'Клиент обновлён!'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('mailing:client_detail', kwargs={'pk': self.object.pk})


class ClientDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    context_object_name = 'client'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


# ============================================================
# Сообщения
# ============================================================

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_manager or user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        user = self.request.user
        if user.is_manager or user.is_superuser:
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_message = 'Сообщение «%(subject)s» добавлено!'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mailing:message_detail', kwargs={'pk': self.object.pk})


class MessageUpdateView(LoginRequiredMixin, OwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_message = 'Сообщение обновлено!'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('mailing:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    context_object_name = 'message'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


# ============================================================
# Рассылки
# ============================================================

class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        qs = Mailing.objects.select_related('message')
        if user.is_manager or user.is_superuser:
            return qs
        return qs.filter(owner=user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        user = self.request.user
        qs = Mailing.objects.select_related('message')
        if user.is_manager or user.is_superuser:
            return qs
        return qs.filter(owner=user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_message = 'Рассылка создана!'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mailing:mailing_detail', kwargs={'pk': self.object.pk})


class MailingUpdateView(LoginRequiredMixin, OwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_message = 'Рассылка обновлена!'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('mailing:mailing_detail', kwargs={'pk': self.object.pk})


class MailingDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    context_object_name = 'mailing'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingSendView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            mailing = Mailing.objects.get(pk=pk)
        except Mailing.DoesNotExist:
            messages.error(request, 'Рассылка не найдена.')
            return redirect('mailing:mailing_list')

        if mailing.owner != request.user and not (request.user.is_manager or request.user.is_superuser):
            messages.error(request, 'У вас нет прав на отправку этой рассылки.')
            return redirect('mailing:mailing_list')

        result = send_mailing(mailing.pk)

        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])

        return redirect('mailing:mailing_detail', pk=mailing.pk)


# ============================================================
# Статистика (с кэшем)
# ============================================================

class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailing/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Кэш для статистики (только счётчики, не таблица)
        if user.is_manager or user.is_superuser:
            cache_key = 'stats_manager'
        else:
            cache_key = f'stats_user_{user.pk}'

        stats = cache.get(cache_key)

        if stats is None:
            if user.is_manager or user.is_superuser:
                qs_mailings = Mailing.objects.all()
                qs_attempts = MailingAttempt.objects.all()
            else:
                qs_mailings = Mailing.objects.filter(owner=user)
                qs_attempts = MailingAttempt.objects.filter(mailing__owner=user)

            stats = {
                'total_mailings': qs_mailings.count(),
                'total_attempts': qs_attempts.count(),
                'success_attempts': qs_attempts.filter(status=MailingAttempt.STATUS_SUCCESS).count(),
                'failed_attempts': qs_attempts.filter(status=MailingAttempt.STATUS_FAILED).count(),
            }
            cache.set(cache_key, stats, timeout=settings.CACHE_TTL_STATS)

        context.update(stats)

        # Таблицу не кэшируем (она обновляется часто)
        if user.is_manager or user.is_superuser:
            qs_attempts = MailingAttempt.objects.all()
        else:
            qs_attempts = MailingAttempt.objects.filter(mailing__owner=user)

        context['recent_attempts'] = qs_attempts.select_related(
            'mailing', 'mailing__message'
        ).order_by('-attempt_time')[:20]

        return context

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response['Cache-Control'] = 'private, max-age=60'
        return response
