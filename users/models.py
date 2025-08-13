from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Менеджер для модели CustomUser.

    Этот класс управляет созданием пользователей и суперпользователей,
    а также нормализацией номера телефона.

    Методы:
        create_user(phone_number, password=None, **extra_fields): Создает и возвращает нового пользователя.
        create_superuser(phone_number, password=None, **extra_fields): Создает и возвращает нового суперпользователя.
        normalize_phone_number(phone_number): Нормализует номер телефона, удаляя лишние пробелы.
    """
    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Создает нового пользователя с указанным номером телефона и паролем.

        Args:
            phone_number (str): Номер телефона для нового пользователя.
            password (str, optional): Пароль для нового пользователя. По умолчанию None.
            **extra_fields: Дополнительные поля, которые могут быть установлены для пользователя.

        Raises:
            ValueError: Если номер телефона не указан.

        Returns:
            CustomUser: Созданный объект пользователя.
        """
        if not phone_number:
            raise ValueError("The phone_number field must be set")
        phone_number = self.normalize_phone_number(phone_number)
        user = self.model(email=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        Создает нового суперпользователя с указанным номером телефона и паролем.

        Args:
            phone_number (str): Номер телефона для суперпользователя.
            password (str, optional): Пароль для суперпользователя. По умолчанию None.
            **extra_fields: Дополнительные поля, которые могут быть установлены для суперпользователя.

        Returns:
            CustomUser: Созданный объект суперпользователя.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(phone_number, password, **extra_fields)

    def normalize_phone_number(self, phone_number):
        return self.create_user(phone_number, password, **extra_fields)

    def normalize_phone_number(self, phone_number):
        return phone_number.strip()


class CustomUser(AbstractUser):
    """
    Модель пользовательской учетной записи.

    Эта модель расширяет стандартную модель пользователя Django,
    убирая поле username и добавляя поля для номера телефона, аватара и других атрибутов.

    Атрибуты:
        username (str): Убирается из модели (заменяется на phone_number).
        phone_number (str): Номер телефона, уникальный для каждого пользователя.
        avatar (ImageField): Изображение профиля пользователя (необязательное поле).
        email (EmailField): Электронная почта, уникальная для каждого пользователя.
        country (str): Страна пользователя (необязательное поле).
        is_blocked (bool): Указывает, заблокирован ли пользователь.
        has_paid_subscription (bool): Указывает, имеет ли пользователь оплаченные подписки.
    """

    username = None
    phone_number = models.CharField(max_length=15, unique=True, null=False, blank=False)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    has_paid_subscription = models.BooleanField(default=False)

    class Meta:
        """
        Метаданные модели CustomUser.

        Этот класс определяет разрешения для модели CustomUser,
        такие как возможность просмотра и блокировки пользователей.
        """
        permissions = [
            ("can_view_users", "Can view users"),
            ("can_block_user", "Can block users"),
        ]

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
