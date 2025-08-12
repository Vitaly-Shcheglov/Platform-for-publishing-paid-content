from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Payment
from rest_framework import status
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
from .serializers import PaymentSerializer


class PaymentListView(generics.ListAPIView):
    """
    View для получения списка всех платежей.

    Этот класс предоставляет API для получения списка всех платежей,
    доступных только для авторизованных пользователей.
    Пользователи могут фильтровать платежи по посту и методу оплаты.

    Атрибуты:
        queryset (QuerySet): Запрос для получения всех объектов Payment.
        serializer_class (Serializer): Сериализатор, который используется для представления данных Payment.
        permission_classes (list): Список разрешений, определяющих доступ к представлению.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает отфильтрованный список платежей на основе параметров запроса.

        Этот метод позволяет фильтровать платежи по ID поста и методу оплаты,
        если соответствующие параметры переданы в запросе.

        Args:
            None

        Returns:
            QuerySet: Отфильтрованный список платежей, соответствующих параметрам запроса.
        """
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post_id', None)
        payment_method = self.request.query_params.get('payment_method', None)

        if post_id_id:
            queryset = queryset.filter(paid_post_id=post_id)
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        return queryset


class PaymentCreateView(APIView):
    """
    View для создания платежа.

    Позволяет пользователю создать платеж за пост, создавая цену в Stripe,
    а также сессию для получения ссылки на оплату.

    Атрибуты:
        permission_classes (list): Список разрешений, определяющих доступ к представлению.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает создание платежа.

        Этот метод ожидает, что в запросе будут переданы данные о платеже,
        такие как сумма, тип подписки и идентификатор поста.

            Args:
            request (Request): Объект запроса с данными о платеже.
            *args: Дополнительные аргументы (не используются).
            **kwargs: Дополнительные именованные аргументы (не используются).

        Returns:
            Response: Ответ с информацией о сессии для оплаты.
                Если данные некорректны, возвращает ошибку с соответствующим статусом.
        """
        amount = request.data.get('amount')
        is_subscription = request.data.get('is_subscription', False)
        subscription_type = request.data.get('subscription_type')  # 'basic' или 'premium'

        if subscription_type == 'basic':
            price = create_price('prod_existing_id', 500)  # 5.00 USD
        elif subscription_type == 'premium':
            price = create_price('prod_existing_id', 1000)  # 10.00 USD
        else:
            return Response({"error": "Invalid subscription type"}, status=status.HTTP_400_BAD_REQUEST)

        session = create_checkout_session(price.id)

        Payment.objects.create(
            user=request.user,
            amount=amount,
            payment_method='stripe',
            is_subscription=True,
        )

        return Response({"url": session.url}, status=status.HTTP_201_CREATED)


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    """
    Обрабатывает вебхуки от Stripe.

    Эта функция обрабатывает входящие вебхуки от Stripe, проверяет подпись и обновляет
    статус платежа в базе данных. В зависимости от типа события, она либо обновляет статус
    платежа на 'succeeded', либо на 'failed'.

    Args:
        request (HttpRequest): Объект запроса от Stripe, содержащий данные о событии.

    Returns:
        HttpResponse: Возвращает HTTP ответ с кодом 200 в случае успешной обработки,
                        или код 400 в случае ошибок валидации или подписи.
    """
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        payment_id = payment_intent['id']
        amount_received = payment_intent['amount_received'] / 100
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_id)
            payment.status = 'succeeded'
            payment.save()
        except Payment.DoesNotExist:
            return HttpResponse(status=404)

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        payment_id = payment_intent['id']
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_id)
            payment.status = 'failed'
            payment.save()
        except Payment.DoesNotExist:
            return HttpResponse(status=404)

    return HttpResponse(status=200)
