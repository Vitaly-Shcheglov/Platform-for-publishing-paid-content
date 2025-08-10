from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Payment
from users.models import CustomUser
from posts.models import Post
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import CustomUser
from .forms import UserRegistrationForm

User = get_user_model()


class PaymentViewsTest(TestCase):
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

        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post.',
            is_published=True,
            owner=self.user
        )

        self.payment = Payment.objects.create(
            user=self.user,
            paid_post=self.post,
            amount=100.00,
            payment_method='cash',
            is_subscription=False,
            stripe_payment_intent_id='test_intent_id'
        )

    def test_payment_list_view(self):
        """Тест для проверки получения списка платежей."""
        response = self.client.get(reverse('payment_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_payment_create_view(self):
        """Тест для создания нового платежа."""
        response = self.client.post(reverse('payment_create'), data={
            'amount': 100.00,
            'paid_post': self.post.id,
            'payment_method': 'cash',
            'is_subscription': False,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Payment.objects.filter(user=self.user, amount=100.00).exists())

    def test_stripe_webhook(self):
        """Тест для проверки обработки вебхука Stripe."""
        payload = {
            "id": "evt_test",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "test_intent_id",
                    "amount_received": 10000,
                }
            }
        }

        response = self.client.post(reverse('stripe_webhook'), data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment = Payment.objects.get(stripe_payment_intent_id="test_intent_id")
        self.assertEqual(payment.status, 'succeeded')


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            phone_number='1234567890',
            country='Russia'
        )

    def test_user_registration_view(self):
        """Тест для проверки регистрации пользователя."""
        response = self.client.post(reverse('register'), data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone_number': '0987654321',
            'country': 'USA',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        """Тест для проверки входа пользователя."""
        response = self.client.post(reverse('login'), data={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.wsgi_request.user, self.user)

    def test_profile_edit_view(self):
        """Тест для проверки редактирования профиля."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('profile_edit'), data={
            'phone_number': '9876543210',
            'country': 'Canada',
            'avatar': '',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, '9876543210')

    def test_user_list_view(self):
        """Тест для проверки списка пользователей."""
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_block_user(self):
        """Тест для проверки блокировки и разблокировки пользователя."""
        self.client.login(username='testuser', password='password123')
        user_to_block = User.objects.create_user(
            username='blockuser',
            email='blockuser@example.com',
            password='password123'
        )
        response = self.client.post(reverse('block_user', kwargs={'user_id': user_to_block.id}))
        self.assertEqual(response.status_code, 302)
        user_to_block.refresh_from_db()
        self.assertTrue(user_to_block.is_blocked)
