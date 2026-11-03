from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Создаёт группу «Менеджер» с правами на просмотр'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Менеджер')
        if created:
            self.stdout.write(self.style.SUCCESS('Группа «Менеджер» создана.'))
        else:
            self.stdout.write('Группа «Менеджер» уже существует.')

        perms = Permission.objects.filter(
            codename__in=[
                'view_client', 'view_message', 'view_mailing', 'view_mailingattempt',
                'change_user',
            ]
        )
        group.permissions.set(perms)
        self.stdout.write(self.style.SUCCESS(f'Назначено прав: {perms.count()}'))
