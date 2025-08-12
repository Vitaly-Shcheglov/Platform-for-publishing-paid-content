from django.core.cache import cache
from .models import Post
import stripe


class PostService:
    @staticmethod
    def get_posts_by_category(category_id):
        """Возвращает список всех записей в указанной категории с кэшированием."""
        cache_key = f"poss_in_category_{category_id}"
        posts = cache.get(cache_key)

        if posts is None:
            posts = Post.objects.filter(category_id=category_id)
            cache.set(cache_key, posts, 60 * 15)

        return posts
