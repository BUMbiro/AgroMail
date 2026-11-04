from django.contrib import admin

from .models import Client, Message, Mailing, MailingAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('email', 'full_name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('subject', 'body')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'status', 'start_time', 'end_time', 'owner')
    list_filter = ('status', 'owner')
    search_fields = ('message__subject',)
    filter_horizontal = ('recipients',)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'mailing', 'status', 'attempt_time')
    list_filter = ('status',)
    search_fields = ('server_response',)
    readonly_fields = ('attempt_time',)
