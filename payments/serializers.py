from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.

    Этот сериализатор преобразует объекты Payment в формат JSON и обратно.
    Он также позволяет управлять данными о платежах пользователей,
    обеспечивая валидацию и сериализацию.

    Поля:
        id (int): Уникальный идентификатор платежа.
        user (User): Пользователь, который совершил платеж.
                     Ссылается на модель пользователя.
        payment_date (datetime): Дата и время, когда был совершен платеж.
        paid_post (Post): Пост, за который был осуществлен платеж.
                          Может быть пустым, если платеж не связан с конкретным постом.
        amount (Decimal): Сумма платежа в минимальных единицах валюты (например, копейки).
        payment_method (str): Метод оплаты, использованный для транзакции (например, 'stripe').
        is_subscription (bool): Указывает, является ли данный платеж подпиской.
    """
    class Meta:
        model = Payment
        fields = ['id', 'user', 'payment_date', 'paid_post', 'amount', 'payment_method', 'is_subscription']
