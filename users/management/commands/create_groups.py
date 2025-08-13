from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from users.models import CustomUser


class Command(BaseCommand):
    """
    Команда для создания групп с определенными разрешениями.

    Этот класс создает группу "Post moderator group" и назначает ей
    определенные разрешения. Также он добавляет пользователя в созданную группу.

    Атрибуты:
        help (str): Описание команды, которое будет отображаться в справке.
    """
    help = "Create groups with specific permissions"

    def handle(self, *args, **kwargs):
        """
        Выполняет команду для создания группы и назначения разрешений.

        Этот метод создает группу "Post moderator group", если она не
        существует, и добавляет к ней определенные разрешения. Затем
        он добавляет указанного пользователя в эту группу.

        Args:
            *args: Позиционные аргументы, переданные в команду.
            **kwargs: Именованные аргументы, переданные в команду.

        Returns:
        None: Метод не возвращает значения, но выводит сообщение об успехе.
        """
        post_moderator_group, created = Group.objects.get_or_create(name="Post moderator group")
        can_unpublish_permission = Permission.objects.get(codename="can_unpublish_post")
        can_delete_permission = Permission.objects.get(codename="can_delete_post")
        can_view_users = Permission.objects.get(codename="can_view_users")
        can_block_user = Permission.objects.get(codename="can_block_user")

        post_moderator_group.permissions.add(can_unpublish_permission, can_delete_permission, can_view_users,
                                             can_block_user, )

        user = CustomUser.objects.get(
            phone_number="89090249875"
        )  # Замените на фактический phone_number зарегистрированного пользователя

        user.groups.add(post_moderator_group)

        self.stdout.write(self.style.SUCCESS("Successfully created groups and assigned permissions."))
