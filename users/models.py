from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Менеджер для модели CustomUser.

    Этот класс управляет созданием пользователей и суперпользователей,
    а также нормализацией номера телефона.

    Методы:
        create_user(phone_number, password=None, **extra_fields): Создает нового пользователя.
        create_superuser(phone_number, password=None, **extra_fields): Создает нового суперпользователя.
        normalize_phone_number(phone_number): Нормализует номер телефона.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Создает нового пользователя с указанным номером телефона и паролем.

        Args:
            phone_number (str): Номер телефона для нового пользователя.
                Должен быть уникальным и не может быть пустым.
            password (str, optional): Пароль для нового пользователя.
                Если не указан, будет установлен в None.
            **extra_fields: Дополнительные поля, которые могут быть установлены для пользователя.

        Raises:
            ValueError: Если номер телефона не указан.

        Returns:
            CustomUser: Созданный объект пользователя.
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

        Суперпользователь имеет права администрирования и доступ ко всем функциям.

        Args:
            phone_number (str): Номер телефона для суперпользователя.
                Должен быть уникальным и не может быть пустым.
            password (str, optional): Пароль для суперпользователя.
                Если не указан, будет установлен в None.
            **extra_fields: Дополнительные поля, которые могут быть установлены для суперпользователя.

        Returns:
            CustomUser: Созданный объект суперпользователя.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(phone_number, password, **extra_fields)

    def normalize_phone_number(self, phone_number):
        """
        Нормализует номер телефона, удаляя лишние пробелы.

        Args:
            phone_number (str): Номер телефона, который необходимо нормализовать.

        Returns:
            str: Нормализованный номер телефона без пробелов.
        """
        return phone_number.strip().replace(" ", "")


class CustomUser(AbstractUser):
    """
    Модель пользовательской учетной записи.

    Этот класс расширяет стандартную модель пользователя Django,
    убирая поле username и добавляя телефонный номер и другие поля.

    Атрибуты:
        phone_number (str): Уникальный номер телефона пользователя.
        avatar (ImageField): Аватар пользователя, загружаемый в директорию "avatars/".
        is_blocked (bool): Флаг, указывающий, заблокирован ли пользователь.
        has_paid_subscription (bool): Флаг, указывающий, есть ли у пользователя платная подписка.

    Метаданные:
        permissions: Дополнительные разрешения для управления пользователями.
    """

    username = None
    phone_number = models.CharField(max_length=15, unique=True, null=False, blank=False)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
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
