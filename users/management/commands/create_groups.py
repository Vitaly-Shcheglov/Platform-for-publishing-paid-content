from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from users.models import CustomUser


class Command(BaseCommand):
    help = "Create groups with specific permissions"

    def handle(self, *args, **kwargs):
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
