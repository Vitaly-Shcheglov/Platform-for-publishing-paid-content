from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def deactivate_inactive_users():
    """
    Периодическая задача, которая блокирует пользователей, не заходивших в систему более месяца.
    """
    one_month_ago = timezone.now() - timezone.timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)

    for user in inactive_users:
        user.is_active = False
        user.save()
        print(f"Пользователь {user.email} был заблокирован.")
