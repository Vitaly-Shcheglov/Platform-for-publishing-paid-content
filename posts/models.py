from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    """
    Модель категории.

    Эта модель представляет собой категорию, к которой могут относиться посты.
    Каждая категория может иметь описание и может быть связана с родительской категорией.

    Атрибуты:
        name (str): Название категории.
        description (str): Описание категории (необязательное поле).
        parent (ForeignKey): Ссылка на родительскую категорию (если есть).
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)


    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        """
        Возвращает строковое представление категории.

        Returns:
            str: Название категории.
        """
        return self.name


class Subcategory(models.Model):
    """
    Модель подкатегории.

    Эта модель представляет собой подкатегорию, связанная с основной категорией.
    Подкатегории могут быть использованы для более детальной классификации постов.

    Атрибуты:
        name (str): Название подкатегории.
        category (ForeignKey): Ссылка на основную категорию, к которой принадлежит подкатегория.
    """

    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"

    def __str__(self):
        """
        Возвращает строковое представление подкатегории.

        Returns:
            str: Название подкатегории.
        """
        return self.name


class Post(models.Model):
    """
    Модель поста.

    Эта модель представляет собой пост, который может содержать текстовое содержание,
    принадлежать к категории и подкатегории, и иметь информацию о пользователе,
    который его создал.

    Атрибуты:
        title (str): Заголовок поста.
        content (str): Содержание поста.
        category (ForeignKey): Ссылка на категорию, к которой принадлежит пост.
        subcategory (ForeignKey): Ссылка на подкатегорию, к которой принадлежит пост (необязательное поле).
        author (ForeignKey): Ссылка на автора поста.
        created_at (DateTimeField): Дата и время создания поста, устанавливается автоматически.
        updated_at (DateTimeField): Дата и время последнего обновления поста, обновляется автоматически.
        owner (ForeignKey): Ссылка на пользователя, который является владельцем поста.
        is_published (bool): Указывает, опубликован ли пост.
        is_paid (bool): Указывает, является ли пост платным.
        image (ImageField): Изображение, связанное с постом (необязательное поле).
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts")
    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.CASCADE, related_name="post_subcategories", null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="uploads/", null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)

    class Meta:
        """
        Метаданные модели Post.

        Этот класс определяет дополнительные параметры для модели Post, такие как
        отображаемые имена в административной панели и разрешения для модели.

        Атрибуты:
            verbose_name (str): Человекочитаемое имя модели в единственном числе.
            verbose_name_plural (str): Человекочитаемое имя модели во множественном числе.
            permissions (tuple): Кортеж разрешений, связанных с моделью.
        """

        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        permissions = (
            ("can_unpublish_post", "Может отменять публикацию записи"),
            ("can_delete_post", "Может удалять запись"),
        )

    def __str__(self):
        """
        Возвращает строковое представление поста.

        Returns:
            str: Заголовок поста, который используется для отображения объекта в админ-панели и других местах.
        """
        return self.title


class Subscription(models.Model):
    """
    Модель подписки пользователя.

    Эта модель представляет подписку, которую пользователь может активировать
    для получения доступа к определенным функциям или контенту.

    Атрибуты:
        user (User): Пользователь, к которому относится подписка.
        plan (str): План подписки (например, 'basic' или 'premium').
        start_date (datetime): Дата начала подписки. Устанавливается автоматически при создании.
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
        """
        Возвращает строковое представление подписки.

        Формат: "имя пользователя - план подписки - Активная/Неактивная".

        Returns:
            str: Строковое представление подписки с именем пользователя и статусом.
        """
        return f"{self.user.username} - {self.plan} - {'Active' if self.is_active else 'Inactive'}"

    def is_subscription_active(self):
        """
        Проверяет, активна ли подписка.

        Возвращает True, если подписка активна и дата окончания больше текущей даты,
        иначе возвращает False.

        Returns:
            bool: True, если подписка активна, иначе False.
        """
        return self.is_active and self.end_date > timezone.now()
