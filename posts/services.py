from django.core.cache import cache

from .models import Post


class PostService:
    """
    Класс для управления постами.

    Этот класс содержит статические методы для работы с постами, включая
    получение постов по категориям с использованием кэширования.

    Методы:
        get_posts_by_category(category_id): Возвращает список постов в указанной категории с кэшированием.
    """

    @staticmethod
    def get_posts_by_category(category_id):
        """
        Возвращает список всех записей в указанной категории с кэшированием.

        Этот метод проверяет кэш на наличие постов в указанной категории. Если посты
        не найдены в кэше, выполняется запрос к базе данных, и результат кэшируется на 15 минут.

        Args:
            category_id (int): Идентификатор категории, для которой нужно получить посты.

        Returns:
            QuerySet: Список постов в указанной категории.
        """

        cache_key = f"poss_in_category_{category_id}"
        posts = cache.get(cache_key)

        if posts is None:
            posts = Post.objects.filter(category_id=category_id)
            cache.set(cache_key, posts, 60 * 15)

        return posts
