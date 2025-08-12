from django.test import TestCase
from .models import Category, Subcategory, Post, Subscription
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .services import PostService
from django.urls import reverse
from .models import Post, CustomUser, Category, Subcategory
from .forms import PostForm


User = get_user_model()

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", description="Test Description")

    def test_str(self):
        self.assertEqual(str(self.category), "Test Category")

class SubcategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.subcategory = Subcategory.objects.create(name="Test Subcategory", category=self.category)

    def test_str(self):
        self.assertEqual(str(self.subcategory), "Test Subcategory")

class PostModelTest(TestCase):
    def setUp(self):
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
        self.assertEqual(str(self.post), "Test Post")

class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.subscription = Subscription.objects.create(
            user=self.user,
            plan='basic',
            end_date='2025-12-31',
            is_active=True
        )

    def test_str(self):
        self.assertEqual(str(self.subscription), "testuser - basic - Active")

    def test_is_subscription_active(self):
        self.assertTrue(self.subscription.is_subscription_active())

    def test_inactive_subscription(self):
        self.subscription.is_active = False
        self.subscription.save()
        self.assertFalse(self.subscription.is_subscription_active())


class PostServiceTest(TestCase):
    def setUp(self):
        self.category_id = 1
        self.post1 = Post.objects.create(title="Post 1", content="Content 1", category_id=self.category_id)
        self.post2 = Post.objects.create(title="Post 2", content="Content 2", category_id=self.category_id)

    def tearDown(self):
        cache.clear()

    def test_get_posts_by_category_caches_results(self):
        posts = PostService.get_posts_by_category(self.category_id)
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0].title, "Post 1")
        self.assertEqual(posts[1].title, "Post 2")


        cached_posts = cache.get(f"poss_in_category_{self.category_id}")
        self.assertIsNotNone(cached_posts)
        self.assertEqual(len(cached_posts), 2)

    def test_get_posts_by_category_returns_cached_results(self):
        PostService.get_posts_by_category(self.category_id)

        Post.objects.all().delete()

        posts = PostService.get_posts_by_category(self.category_id)
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0].title, "Post 1")
        self.assertEqual(posts[1].title, "Post 2")

    def test_get_posts_by_category_with_non_existent_category(self):
        posts = PostService.get_posts_by_category(999)
        self.assertEqual(len(posts), 0)


class HomeViewTest(TestCase):
    def setUp(self):
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
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/home.html')
        self.assertContains(response, 'Test Post')

class ContactViewTest(TestCase):
    def test_contact_view_get(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/contacts.html')

    def test_contact_view_post_success(self):
        response = self.client.post(reverse('contact'), {
            'name': 'John Doe',
            'phone': '1234567890',
            'message': 'Hello!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Спасибо, John Doe! Ваше сообщение получено.")

    def test_contact_view_post_failure(self):
        response = self.client.post(reverse('contact'), {
            'name': '',
            'phone': '',
            'message': ''
        })
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Пожалуйста, заполните все поля!")

class PostDetailViewTest(TestCase):
    def setUp(self):
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
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/post_detail.html')
        self.assertContains(response, 'Test Post')

class AddPostViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = Subcategory.objects.create(name='Test Subcategory', category=self.category)

    def test_add_post_view(self):
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
    def setUp(self):
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
