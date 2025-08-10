from django.core.management import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    """Команда для создания суперпользователя."""

    def handle(self, *args, **options):
        user = CustomUser.objects.create(
            phone_number="01234567890",  # Замените на фактический phone_number зарегистрированного пользователя
            email="test@example.com" # Замените на фактический email зарегистрированного пользователя
        )
        user.set_password("test")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS('Суперпользователь успешно создан.'))
