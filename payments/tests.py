from posts.models import Post
from django.test import TestCase
from users.models import CustomUser
from .serializers import PaymentSerializer
from unittest.mock import patch
from .services import create_product, create_price, create_checkout_session, create_subscription
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Payment


class PaymentModelTest(TestCase):
    """
    Тесты для модели Payment.

    Этот класс содержит тесты, которые проверяют функциональность и целостность модели Payment.
    """
    def setUp(self):
        """
        Настраивает тестовые данные перед выполнением каждого теста.

        Создает тестового пользователя, тестовый пост и тестовый платеж для использования в тестах.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            phone_number='1234567890',
            country='Russia'
        )

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

    def test_payment_str(self):
        """
        Тест для метода str модели Payment.

        Проверяет, возвращает ли метод str() правильное строковое представление объекта Payment.
        """
        expected_str = f"{self.user.username} - {self.payment.amount} - {self.payment.payment_method}"
        self.assertEqual(str(self.payment), expected_str)

    def test_payment_creation(self):
         """
        Тест для проверки создания платежа.

        Проверяет, что созданный платеж имеет корректные атрибуты.
        """
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.paid_post, self.post)
        self.assertEqual(self.payment.amount, 100.00)
        self.assertEqual(self.payment.payment_method, 'cash')
        self.assertFalse(self.payment.is_subscription)
        self.assertEqual(self.payment.status, 'pending')
        self.assertIsNotNone(self.payment.payment_date)

    def test_payment_method_choices(self):
        """
        Тест для проверки выбора метода оплаты.

        Проверяет, что метод оплаты в созданном платеже соответствует допустимым методам,
        определенным в классе Payment.
        """
        valid_methods = dict(Payment.PAYMENT_METHODS).keys()
        self.assertIn(self.payment.payment_method, valid_methods)

    def test_subscription_payment(self):
        """
        Тест для проверки создания подписки.

        Проверяет, что созданный платеж для подписки имеет правильные атрибуты.
        """
        subscription_payment = Payment.objects.create(
            user=self.user,
            paid_post=self.post,
            amount=200.00,
            payment_method='stripe',
            is_subscription=True,
            stripe_payment_intent_id='test_intent_id_2'
        )
        self.assertTrue(subscription_payment.is_subscription)
        self.assertEqual(subscription_payment.amount, 200.00)
        self.assertEqual(subscription_payment.payment_method, 'stripe')


class PaymentSerializerTest(TestCase):
    """
    Тесты для сериализатора PaymentSerializer.

    Этот класс содержит тесты, которые проверяют функциональность сериализатора PaymentSerializer.
    """
    def setUp(self):
        """
        Настраивает тестовые данные для тестирования сериализатора.

        Создает тестового пользователя и тестовый платеж для использования в тестах сериализатора.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            phone_number='1234567890',
            country='Russia'
        )

        self.payment = Payment.objects.create(
            user=self.user,
            amount=100.00,
            payment_method='cash',
            is_subscription=False,
            stripe_payment_intent_id='test_intent_id'
        )

    def test_payment_serializer(self):
        """
        Тест для проверки сериализации модели Payment.

        Проверяет, правильно ли сериализуются данные модели Payment в формат JSON.
        """
        serializer = PaymentSerializer(instance=self.payment)
        data = serializer.data

        self.assertEqual(data['id'], self.payment.id)
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['amount'], str(self.payment.amount))
        self.assertEqual(data['payment_method'], self.payment.payment_method)
        self.assertEqual(data['is_subscription'], self.payment.is_subscription)

    def test_payment_serializer_validation(self):
        """
        Тест для проверки валидации сериализатора PaymentSerializer.

        Этот тест проверяет, что сериализатор корректно обрабатывает
        валидные данные для создания объекта Payment. Он также
        проверяет, что созданный объект имеет правильные атрибуты.

        Args:
            None

        Returns:
            None
        """
        serializer = PaymentSerializer(data={
            'user': self.user.id,
            'amount': 200.00,
            'payment_method': 'transfer',
            'is_subscription': True,
            'stripe_payment_intent_id': 'new_intent_id'
        })
        self.assertTrue(serializer.is_valid())
        payment = serializer.save()
        self.assertEqual(payment.amount, 200.00)
        self.assertEqual(payment.payment_method, 'transfer')

    def test_payment_serializer_invalid(self):
        """
        Тест для проверки валидации сериализатора PaymentSerializer.

        Этот тест проверяет, что сериализатор корректно обрабатывает
        валидные данные для создания объекта Payment. Он также
        проверяет, что созданный объект имеет правильные атрибуты.

        Args:
            None

        Returns:
            None
        """
        serializer = PaymentSerializer(data={
            'user': None,
            'amount': -50.00,
            'payment_method': 'unknown_method',
            'is_subscription': False
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)
        self.assertIn('amount', serializer.errors)
        self.assertIn('payment_method', serializer.errors)


class StripeServiceTests(TestCase):
    """
    Тесты для функций, связанных с Stripe.

    Этот класс содержит тесты для создания продуктов, цен и сессий оплаты через Stripe.
    """

    @patch('stripe.Product.create')
    def test_create_product(self, mock_create):
        """
        Тест для проверки создания продукта в Stripe.

        Проверяет, что функция create_product корректно создает продукт в Stripe
        и возвращает ожидаемые данные.

        Args:
            mock_create (MagicMock): Заглушка для метода create из Stripe API.

        Returns:
            None
        """
        mock_create.return_value = {'id': 'prod_test', 'name': 'Test Product', 'description': 'Test Description'}

        product = create_product("Test Product", "Test Description")

        self.assertEqual(product['id'], 'prod_test')
        self.assertEqual(product['name'], 'Test Product')
        self.assertEqual(product['description'], 'Test Description')
        mock_create.assert_called_once_with(name="Test Product", description="Test Description")

    @patch('stripe.Price.create')
    def test_create_price(self, mock_create):
        """
        Тест для проверки создания цены в Stripe.

        Проверяет, что функция create_price корректно создает цену для продукта
        в Stripe и возвращает ожидаемые данные.

        Args:
            mock_create (MagicMock): Заглушка для метода create из Stripe API.

        Returns:
            None
        """
        mock_create.return_value = {'id': 'price_test', 'unit_amount': 1000}

        price = create_price('prod_test', 1000)

        self.assertEqual(price['id'], 'price_test')
        mock_create.assert_called_once_with(unit_amount=1000, currency='usd', product='prod_test')

    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_create):
        """
        Тест для проверки создания сессии оплаты в Stripe.

        Проверяет, что функция create_checkout_session корректно создает сессию оплаты
        и возвращает ожидаемые данные.

        Args:
            mock_create (MagicMock): Заглушка для метода create из Stripe API.

        Returns:
            None
        """
        mock_create.return_value = {'id': 'session_test', 'url': 'http://localhost:8000/session'}

        session = create_checkout_session('price_test')

        self.assertEqual(session['id'], 'session_test')
        self.assertEqual(session['url'], 'http://localhost:8000/session')
        mock_create.assert_called_once()

    @patch('your_module.create_product')
    @patch('your_module.create_price')
    @patch('your_module.create_checkout_session')
    def test_create_subscription(self, mock_checkout_session, mock_create_price, mock_create_product):
        """
        Тест для проверки создания подписки.

        Проверяет, что функция create_subscription корректно создает сессию для подписки
        и возвращает ожидаемую URL сессии оплаты.

        Args:
            mock_checkout_session (MagicMock): Заглушка для метода create_checkout_session.
            mock_create_price (MagicMock): Заглушка для метода create_price.
            mock_create_product (MagicMock): Заглушка для метода create_product.

        Returns:
            None
        """
        mock_create_product.return_value = {'id': 'prod_test'}
        mock_create_price.return_value = {'id': 'price_test'}
        mock_checkout_session.return_value = {'url': 'http://localhost:8000/session'}

        user = 'test_user'
        amount = 1000

        session = create_subscription(user, amount)

        self.assertEqual(session['url'], 'http://localhost:8000/session')
        mock_create_product.assert_called_once_with(name="Разовая подписка", description="Оплата за разовую подписку")
        mock_create_price.assert_called_once_with('prod_test', amount)
        mock_checkout_session.assert_called_once_with('price_test')


class PaymentViewsTest(TestCase):
     """
    Тесты для представлений, связанных с платежами.

    Этот класс содержит тесты для проверки поведения API, связанного с платежами.
    """
    def setUp(self):
        """
        Настраивает тестовые данные для тестирования представлений.

        Создает тестового пользователя и тестовый пост.
        """
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
        """
        Тест для проверки списка платежей.

        Этот тест проверяет, что API возвращает корректный статус и
        количество платежей в ответе.
        """
        response = self.client.get(reverse('payment_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_payment_create_view(self):
        """
        Тест для создания платежа.

        Этот тест проверяет, что API создает новый платеж и возвращает
        корректный статус и данные в ответе.
        """
        response = self.client.post(reverse('payment_create'), data={
            'amount': 100.00,
            'is_subscription': False,
            'paid_post': self.post.id,
            'payment_method': 'cash',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Payment.objects.filter(user=self.user, amount=100.00).exists())
