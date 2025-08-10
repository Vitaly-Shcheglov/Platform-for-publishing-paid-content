from django.test import TestCase
from django.utils import timezone
from .models import Category, Subcategory, Post, Subscription
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import CustomUser

User = get_user_model()


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_category_str(self):
        """Тест для метода str модели Category."""
        self.assertEqual(str(self.category), "Test Category")


class SubcategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.subcategory = Subcategory.objects.create(name="Test Subcategory", category=self.category)

    def test_subcategory_str(self):
        """Тест для метода str модели Subcategory."""
        self.assertEqual(str(self.subcategory), "Test Subcategory")


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.category = Category.objects.create(name="Test Category")
        self.subcategory = Subcategory.objects.create(name="Test Subcategory", category=self.category)
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post.",
            category=self.category,
            subcategory=self.subcategory,
            author=self.user,
            is_published=True,
        )

    def test_post_str(self):
        """Тест для метода str модели Post."""
        self.assertEqual(str(self.post), "Test Post")

    def test_post_creation(self):
        """Тест для проверки создания поста."""
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.category, self.category)
        self.assertEqual(self.post.subcategory, self.subcategory)
        self.assertTrue(self.post.is_published)
        self.assertIsNotNone(self.post.created_at)


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan="basic",
            end_date=timezone.now() + timezone.timedelta(days=30),
            is_active=True
        )

    def test_subscription_str(self):
        """Тест для метода str модели Subscription."""
        self.assertEqual(str(self.subscription), "testuser - basic - Active")

    def test_is_subscription_active(self):
        """Тест для метода is_subscription_active."""
        self.assertTrue(self.subscription.is_subscription_active())

        self.subscription.is_active = False
        self.subscription.save()
        self.assertFalse(self.subscription.is_subscription_active())


class PostViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            phone_number='1234567890',
            country='Russia'
        )
        self.client.login(username='testuser', password='password123')

        self.category = Category.objects.create(name='Test Category')
        self.subcategory = Subcategory.objects.create(name='Test Subcategory', category=self.category)

        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            category=self.category,
            subcategory=self.subcategory,
            author=self.user,
            is_published=True,
        )

    def test_home_view(self):
        """Тест для проверки отображения главной страницы."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Список публикаций')
        self.assertContains(response, self.post.title)

    def test_contact_view_get(self):
        """Тест для проверки отображения страницы контактов."""
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Контакты')

    def test_contact_view_post(self):
        """Тест для проверки отправки сообщения через форму контактов."""
        response = self.client.post(reverse('contacts'), data={
            'name': 'Test User',
            'phone': '1234567890',
            'message': 'Hello!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Спасибо, Test User! Ваше сообщение получено.")

    def test_post_detail_view(self):
        """Тест для проверки отображения деталей поста."""
        response = self.client.get(reverse('post_detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.post.title)

    def test_add_post_view(self):
        """Тест для проверки добавления нового поста."""
        response = self.client.post(reverse('add_post'), data={
            'title': 'New Post',
            'content': 'Content for new post',
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'is_paid': False,
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertTrue(Post.objects.filter(title='New Post').exists())

    def test_post_update_view(self):
        """Тест для проверки обновления существующего поста."""
        response = self.client.post(reverse('post_edit', kwargs={'pk': self.post.pk}), data={
            'title': 'Updated Post',
            'content': 'Updated content',
            'category': self.category.id,
            'subcategory': self.subcategory.id,
            'is_paid': False,
        })
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post')

    def test_post_delete_view(self):
        """Тест для проверки удаления поста."""
        response = self.client.post(reverse('post_delete', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
