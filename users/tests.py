import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from posts.models import Post

from .models import CustomUser, Payment

User = get_user_model()


class PaymentViewsTest(TestCase):
    """
    Тестовый класс для проверки представлений, связанных с платежами.

    Этот класс наследует от TestCase и использует APIClient для выполнения
    тестовых запросов к API. Тесты включают в себя проверки на получение
    списка платежей, создание нового платежа и обработку вебхука Stripe.

    Атрибуты:
        client (APIClient): Клиент для выполнения запросов к API.
        user (CustomUser): Тестовый пользователь, созданный для выполнения
               запросов.
        post (Post): Тестовый пост, связанный с платежом.
        payment (Payment): Тестовый платеж, созданный для проверки логики
            обработки платежей.
    """

    def setUp(self):
        """
        Подготовка данных для тестов.

        Этот метод выполняется перед каждым тестом и создает необходимые
        объекты, такие как пользователь, пост и платеж. Также выполняется
        авторизация пользователя для выполнения запросов.
        """
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            phone_number="1234567890",
            country="Russia",
        )
        self.client.login(username="testuser", password="password123")

        self.post = Post.objects.create(
            title="Test Post", content="This is a test post.", is_published=True, owner=self.user
        )

        self.payment = Payment.objects.create(
            user=self.user,
            paid_post=self.post,
            amount=100.00,
            payment_method="cash",
            is_subscription=False,
            stripe_payment_intent_id="test_intent_id",
        )

    def test_payment_list_view(self):
        """
        Тест для проверки получения списка платежей.

        Этот тест выполняет GET-запрос к представлению списка платежей и
        проверяет, что ответ имеет статус 200 (OK) и содержит один платеж,
        созданный в методе setUp.

        Проверяемые аспекты:
            - Статус ответа.
            - Количество платежей в ответе.
        """
        response = self.client.get(reverse("payment_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_payment_create_view(self):
        """
        Тест для создания нового платежа.

        Этот тест выполняет POST-запрос к представлению создания платежа с
        необходимыми данными и проверяет, что новый платеж был успешно
        создан в базе данных.

        Проверяемые аспекты:
            - Статус ответа.
            - Существование нового платежа в базе данных.
        """
        response = self.client.post(
            reverse("payment_create"),
            data={
                "amount": 100.00,
                "paid_post": self.post.id,
                "payment_method": "cash",
                "is_subscription": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Payment.objects.filter(user=self.user, amount=100.00).exists())

    def test_stripe_webhook(self):
        """
        Тест для проверки обработки вебхука Stripe.

        Этот тест выполняет POST-запрос к представлению вебхука Stripe с
        полезной нагрузкой, имитирующей успешное завершение платежа.
        Тест проверяет, что ответ имеет статус 200 (OK) и что статус платежа
        в базе данных обновляется на 'succeeded'.

        Проверяемые аспекты:
            - Статус ответа.
            - Обновление статуса платежа в базе данных.
        """
        payload = {
            "id": "evt_test",
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "test_intent_id",
                    "amount_received": 10000,
                }
            },
        }

        response = self.client.post(
            reverse("stripe_webhook"), data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment = Payment.objects.get(stripe_payment_intent_id="test_intent_id")
        self.assertEqual(payment.status, "succeeded")


class UserViewsTest(TestCase):
    """
    Тестовый класс для проверки представлений, связанных с пользователями.

    Этот класс наследует от TestCase и использует Client для выполнения
    тестовых запросов к API. Тесты включают в себя проверки на регистрацию
    пользователя, вход в систему, редактирование профиля, получение списка
    пользователей и блокировку пользователей.

    Атрибуты:
        client (Client): Клиент для выполнения запросов к API.
        user (User): Тестовый пользователь, созданный для выполнения запросов.
    """

    def setUp(self):
        """
        Подготовка данных для тестов.

        Этот метод выполняется перед каждым тестом и создает необходимые
        объекты, такие как пользователь. Клиент инициализируется для
        выполнения тестовых запросов.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            phone_number="1234567890",
            country="Russia",
        )

    def test_user_registration_view(self):
        """
        Тест для проверки регистрации пользователя.

        Этот тест выполняет POST-запрос к представлению регистрации с
        необходимыми данными и проверяет, что новый пользователь был
        успешно создан в базе данных.

        Проверяемые аспекты:
            - Статус ответа должен быть 302 (перенаправление).
            - Новый пользователь должен существовать в базе данных.
        """
        response = self.client.post(
            reverse("register"),
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "phone_number": "0987654321",
                "country": "USA",
                "password": "password123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_view(self):
        """
        Тест для проверки входа пользователя.

        Этот тест выполняет POST-запрос к представлению входа с
        данными пользователя и проверяет, что вход выполнен успешно.

        Проверяемые аспекты:
            - Статус ответа должен быть 302 (перенаправление).
            - В текущем запросе должен быть авторизован пользователь.
        """
        response = self.client.post(reverse("login"), data={"username": "testuser", "password": "password123"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.wsgi_request.user, self.user)

    def test_profile_edit_view(self):
        """
        Тест для проверки редактирования профиля.

        Этот тест выполняет POST-запрос к представлению редактирования
        профиля с новыми данными пользователя и проверяет, что данные
        профиля были успешно обновлены.

        Проверяемые аспекты:
            - Статус ответа должен быть 302 (перенаправление).
            - Номер телефона пользователя должен быть обновлен.
        """
        self.client.login(username="testuser", password="password123")
        response = self.client.post(
            reverse("profile_edit"),
            data={
                "phone_number": "9876543210",
                "country": "Canada",
                "avatar": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "9876543210")

    def test_user_list_view(self):
        """
        Тест для проверки списка пользователей.

        Этот тест выполняет GET-запрос к представлению списка пользователей
        и проверяет, что статус ответа 200 (OK) и что имя текущего пользователя присутствует в ответе.

        Проверяемые аспекты:
            - Статус ответа должен быть 200.
            - Имя пользователя должно содержаться в ответе.
        """
        response = self.client.get(reverse("user_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_block_user(self):
        """
        Тест для проверки блокировки и разблокировки пользователя.

        Этот тест выполняет POST-запрос к представлению блокировки
        пользователя и проверяет, что статус пользователя обновляется
        на заблокированный.

        Проверяемые аспекты:
            - Статус ответа должен быть 302 (перенаправление).
            - Пользователь должен быть заблокирован.
        """
        self.client.login(username="testuser", password="password123")
        user_to_block = User.objects.create_user(
            username="blockuser", email="blockuser@example.com", password="password123"
        )
        response = self.client.post(reverse("block_user", kwargs={"user_id": user_to_block.id}))
        self.assertEqual(response.status_code, 302)
        user_to_block.refresh_from_db()
        self.assertTrue(user_to_block.is_blocked)
