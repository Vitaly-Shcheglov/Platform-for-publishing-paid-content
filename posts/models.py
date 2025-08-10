from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='child_categories'
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    subcategory = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name='post_subcategories',
        null=True,
        blank=True
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_posts')
    is_published = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    image = models.ImageField(upload_to='uploads/', null=True, blank=True)

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        permissions = (
            ("can_unpublish_post", "Может отменять публикацию записи"),
            ("can_delete_post", "Может удалять запись"),
        )

    def __str__(self):
        return self.title


class Subscription(models.Model):
    """
    Модель подписки пользователя.

    Атрибуты:
        user (User): Пользователь, к которому относится подписка.
        plan (str): План подписки (например, 'basic' или 'premium').
        start_date (datetime): Дата начала подписки.
        end_date (datetime): Дата окончания подписки.
        is_active (bool): Флаг, указывающий, является ли подписка активной.
                          По умолчанию - False.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)  # Например, 'basic' или 'premium'
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        """Возвращает строковое представление подписки с именем пользователя и статусом."""
        return f"{self.user.username} - {self.plan} - {'Active' if self.is_active else 'Inactive'}"

    def is_subscription_active(self):
        """Возвращает True, если подписка активна, иначе False."""
        return self.is_active and self.end_date > timezone.now()
