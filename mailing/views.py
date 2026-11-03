from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)

from .models import Client, Message, Mailing
from .forms import ClientForm, MessageForm, MailingForm


# ============================================================
# Главная страница (пока заглушка, расширим на шаге 7)
# ============================================================

class HomeView(TemplateView):
    """Главная страница — заглушка. Счётчики добавим на шаге 7."""
    template_name = 'mailing/home.html'


# ============================================================
# Клиенты
# ============================================================

class ClientListView(LoginRequiredMixin, ListView):
    """Список клиентов текущего пользователя."""
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    """Детальная клиента."""
    model = Client
    template_name = 'mailing/client_detail.html'
    context_object_name = 'client'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание клиента."""
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_message = 'Клиент «%(full_name)s» добавлен!'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mailing:client_detail', kwargs={'pk': self.object.pk})


class ClientUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование клиента."""
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_message = 'Клиент обновлён!'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('mailing:client_detail', kwargs={'pk': self.object.pk})


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление клиента."""
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
    """Список сообщений текущего пользователя."""
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'
    paginate_by = 10

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    """Детальная сообщения."""
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание сообщения."""
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_message = 'Сообщение «%(subject)s» добавлено!'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mailing:message_detail', kwargs={'pk': self.object.pk})


class MessageUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование сообщения."""
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_message = 'Сообщение обновлено!'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('mailing:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление сообщения."""
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
    """Список рассылок текущего пользователя."""
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'
    paginate_by = 10

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user).select_related('message')


class MailingDetailView(LoginRequiredMixin, DetailView):
    """Детальная рассылки. Пересчитывает статус через update_status()."""
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Создание рассылки."""
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


class MailingUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Редактирование рассылки."""
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


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление рассылки."""
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    context_object_name = 'mailing'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)
