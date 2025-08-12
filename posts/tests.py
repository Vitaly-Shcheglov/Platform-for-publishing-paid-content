from django.test import TestCase
from .models import Subscription
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .services import PostService
from django.urls import reverse
from .models import Post, CustomUser, Category, Subcategory


User = get_user_model()

class CategoryModelTest(TestCase):
    """
    Тесты для модели Category.

    Этот класс содержит тесты, которые проверяют функциональность и целостность модели Category.
    """
    def setUp(self):
        """
        Настраивает тестовые данные перед выполнением каждого теста.

        Создает тестовую категорию для использования в тестах.
        """
        self.category = Category.objects.create(name="Test Category", description="Test Description")

    def test_str(self):
        """
        Тест для метода str модели Category.

        Проверяет, возвращает ли метод str() правильное строковое представление объекта Category.
        """
        self.assertEqual(str(self.category), "Test Category")

class SubcategoryModelTest(TestCase):
    """
    Тесты для модели Subcategory.

    Этот класс содержит тесты, которые проверяют функциональность и целостность модели Subcategory.
    """
    def setUp(self):
        """
        Настраивает тестовые данные перед выполнением каждого теста.

        Создает тестовую категорию и подкатегорию для использования в тестах.
        """
        self.category = Category.objects.create(name="Test Category")
        self.subcategory = Subcategory.objects.create(name="Test Subcategory", category=self.category)

    def test_str(self):
        """
        Тест для метода str модели Subcategory.

        Проверяет, возвращает ли метод str() правильное строковое представление объекта Subcategory.
        """
        self.assertEqual(str(self.subcategory), "Test Subcategory")

class PostModelTest(TestCase):
    """
    Тесты для модели Post.

    Этот класс содержит тесты, которые проверяют функциональность и целостность модели Post.
    """
    def setUp(self):
        """
        Настраивает тестовые данные перед выполнением каждого теста.

        Создает тестового пользователя, категорию и пост для использования в тестах.
        """
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            category=self.category,
            author=self.user,
            is_published=True,
            is_paid=False
        )

    def test_str(self):
        """
        Тест для метода str модели Post.

        Проверяет, возвращает ли метод str() правильное строковое представление объекта Post.
        """
        self.assertEqual(str(self.post), "Test Post")

class SubscriptionModelTest(TestCase):
    """
    Тесты для модели Subscription.

    Этот класс содержит тесты, которые проверяют функциональность и целостность модели Subscription.
    """
    def setUp(self):
        """
        Настраивает тестовые данные перед выполнением каждого теста.

        Создает тестового пользователя и подписку для использования в тестах.
        """
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan='basic',
            end_date='2025-12-31',
            is_active=True
        )

    def test_str(self):
        """
        Тест для метода str модели Subscription.

        Проверяет, возвращает ли метод str() правильное строковое представление объекта Subscription.
        """
        self.assertEqual(str(self.subscription), "testuser - basic - Active")

    def test_is_subscription_active(self):
        """
        Тест для проверки активности подписки.

        Проверяет, что метод is_subscription_active() возвращает True для активной подписки.
        """
        self.assertTrue(self.subscription.is_subscription_active())

    def test_inactive_subscription(self):
        """
        Тест для проверки неактивной подписки.

        Проверяет, что метод is_subscription_active() возвращает False для неактивной подписки.
        """
        self.subscription.is_active = False
        self.subscription.save()
        self.assertFalse(self.subscription.is_subscription_active())


class PostServiceTest(TestCase):
    """
    Тесты для класса PostService.

    Этот класс содержит тесты, которые проверяют функциональность методов класса PostService,
    включая получение постов по категории с кэшированием.
    """
    def setUp(self):
        """
        Настраивает тестовые данные перед выполнением каждого теста.

        Создает тестовую категорию и несколько постов для использования в тестах.
        """
        self.category_id = 1
        self.post1 = Post.objects.create(title="Post 1", content="Content 1", category_id=self.category_id)
        self.post2 = Post.objects.create(title="Post 2", content="Content 2", category_id=self.category_id)

    def tearDown(self):
        """
        Очищает кэш после выполнения каждого теста.

        Этот метод вызывается после выполнения тестов для удаления всех кэшированных данных.
        """
        cache.clear()

    def test_get_posts_by_category_caches_results(self):
        """
        Тест для проверки кэширования результатов при получении постов по категории.

        Проверяет, что метод get_posts_by_category возвращает правильное количество постов
        и кэширует результаты.
        """
        posts = PostService.get_posts_by_category(self.category_id)
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0].title, "Post 1")
        self.assertEqual(posts[1].title, "Post 2")


        cached_posts = cache.get(f"poss_in_category_{self.category_id}")
        self.assertIsNotNone(cached_posts)
        self.assertEqual(len(cached_posts), 2)

    def test_get_posts_by_category_returns_cached_results(self):
        """
        Тест для проверки возвращения кэшированных результатов.

        Проверяет, что метод get_posts_by_category возвращает кэшированные посты,
        даже если посты были удалены из базы данных.
        """
        PostService.get_posts_by_category(self.category_id)

        Post.objects.all().delete()

        posts = PostService.get_posts_by_category(self.category_id)
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0].title, "Post 1")
        self.assertEqual(posts[1].title, "Post 2")

    def test_get_posts_by_category_with_non_existent_category(self):
        """
        Тест для проверки получения постов для несуществующей категории.

        Проверяет, что метод get_posts_by_category возвращает пустой список
        для несуществующего идентификатора категории.
        """
        posts = PostService.get_posts_by_category(999)
        self.assertEqual(len(posts), 0)


class HomeViewTest(TestCase):
    """
    Тесты для класса HomeView.

    Этот класс содержит тесты, которые проверяют функциональность домашней страницы
    и отображение постов.
    """
    def setUp(self):
        """
        Настраивает тестовые данные перед выполнением каждого теста.

        Создает тестового пользователя, категорию и пост для использования в тестах.
        """
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = Subcategory.objects.create(name='Test Subcategory', category=self.category)
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            category=self.category,
            subcategory=self.subcategory,
            author=self.user,
            is_published=True
        )

    def test_home_view(self):
        """
        Тест для проверки домашней страницы.

        Проверяет, что домашняя страница возвращает статус 200 и
        использует правильный шаблон, а также содержит необходимый контент.
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/home.html')
        self.assertContains(response, 'Test Post')

class ContactViewTest(TestCase):
    """
    Тесты для класса ContactView.

    Этот класс содержит тесты, которые проверяют функциональность страницы контактов.
    """
    def test_contact_view_get(self):
        """
        Тест для проверки GET-запроса на страницу контактов.

        Проверяет, что страница контактов возвращает статус 200 и
        использует правильный шаблон.
        """
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/contacts.html')

    def test_contact_view_post_success(self):
        """
        Тест для проверки успешного POST-запроса на страницу контактов.

        Проверяет, что сообщение успешно отправляется, когда все поля заполнены.
        """
        response = self.client.post(reverse('contact'), {
            'name': 'John Doe',
            'phone': '1234567890',
            'message': 'Hello!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спасибо, John Doe! Ваше сообщение получено.")

    def test_contact_view_post_failure(self):
        """
        Тест для проверки обработки некорректных данных в POST-запросе на страницу контактов.

        Проверяет, что возвращается ошибка, если обязательные поля не заполнены.
        """
        response = self.client.post(reverse('contact'), {
            'name': '',
            'phone': '',
            'message': ''
        })
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Пожалуйста, заполните все поля!")

class PostDetailViewTest(TestCase):
    """
    Тесты для класса PostDetailView.

    Этот класс содержит тесты, которые проверяют функциональность страницы деталей поста.
    """
    def setUp(self):
        """
        Настраивает тестовые данные перед выполнением каждого теста.

        Создает тестового пользователя, категорию, подкатегорию и пост для использования в тестах.
        """
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = Subcategory.objects.create(name='Test Subcategory', category=self.category)
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            category=self.category,
            subcategory=self.subcategory,
            author=self.user,
            is_published=True
        )

    def test_post_detail_view(self):
        """
        Тест для проверки страницы деталей поста.

        Проверяет, что страница деталей поста возвращает статус 200 и
        использует правильный шаблон, а также содержит необходимый контент.
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/post_detail.html')
        self.assertContains(response, 'Test Post')

class AddPostViewTest(TestCase):
    """
    Тесты для представления добавления поста.

    Этот класс содержит тесты, которые проверяют функциональность представления,
    позволяющего пользователям добавлять новые посты.
    """
    def setUp(self):
        """
        Настраивает тестовые данные перед выполнением каждого теста.

        Создает тестового пользователя, категорию и подкатегорию для использования в тестах.
        """
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = Subcategory.objects.create(name='Test Subcategory', category=self.category)

    def test_add_post_view(self):
        """
        Тест для проверки добавления нового поста.

        Проверяет, что пользователь может успешно добавить новый пост,
        и что после успешного добавления происходит перенаправление.

        Returns:
            None
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('add_post'), {
            'title': 'New Test Post',
            'content': 'Content of the new post.',
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'is_paid': False
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New Test Post').exists())

class PostUpdateViewTest(TestCase):
    """
    Тесты для представления обновления поста.

    Этот класс содержит тесты, которые проверяют функциональность представления,
    позволяющего пользователям обновлять существующие посты.
    """
    def setUp(self):
        """
        Настраивает тестовые данные перед выполнением каждого теста.

        Создает тестового пользователя, категорию, подкатегорию и пост для использования в тестах.
        """
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = Subcategory.objects.create(name='Test Subcategory', category=self.category)
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            category=self.category,
            subcategory=self.subcategory,
            author=self.user,
            is_published=True
        )

    def test_post_update_view(self):
        """
        Тест для проверки обновления существующего поста.

        Проверяет, что пользователь может успешно обновить пост и что после обновления
        происходит перенаправление. Также проверяет, что атрибуты поста обновлены.

        Returns:
            None
        """
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('post_update', args=[self.post.id]), {
            'title': 'Updated Test Post',
            'content': 'Updated content.',
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'is_paid': False
        })
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Test Post')
