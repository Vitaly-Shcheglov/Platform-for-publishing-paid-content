from rest_framework import serializers
from .models import Payment
from django.contrib.auth import get_user_model
from users.models import CustomUser


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.

    Этот сериализатор преобразует объекты Payment в JSON и обратно.
    Позволяет управлять платежами пользователей.
    """
    class Meta:
        model = Payment
        fields = ['id', 'user', 'payment_date', 'paid_post', 'amount', 'payment_method', 'is_subscription']
