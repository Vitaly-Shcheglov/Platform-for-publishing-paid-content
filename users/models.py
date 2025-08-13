from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Менеджер для модели CustomUser.

    Этот класс управляет созданием пользователей и суперпользователей,
    а также нормализацией номера телефона.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Создает нового пользователя с указанным номером телефона и паролем.

        Args:
            phone_number (str): Номер телефона для нового пользователя.
            password (str, optional): Пароль для нового пользователя. По умолчанию None.
            **extra_fields: Дополнительные поля, которые могут быть установлены для пользователя.
        """
        if not phone_number:
            raise ValueError("The phone_number field must be set")
        phone_number = self.normalize_phone_number(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        Создает нового суперпользователя с указанным номером телефона и паролем.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(phone_number, password, **extra_fields)

    def normalize_phone_number(self, phone_number):
        return phone_number.strip().replace(" ", "")


class CustomUser(AbstractUser):
    """
    Модель пользовательской учетной записи.
    """

    username = None
    phone_number = models.CharField(max_length=15, unique=True, null=False, blank=False)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    has_paid_subscription = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("can_view_users", "Can view users"),
            ("can_block_user", "Can block users"),
        ]

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
