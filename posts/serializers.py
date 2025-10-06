from rest_framework import serializers

from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscription.

    Этот сериализатор преобразует объекты Subscription в формат JSON и обратно.
    Он используется для управления данными о подписках пользователей в API.

    Атрибуты:
        user (User): Пользователь, к которому относится подписка.
        plan (str): План подписки (например, 'basic' или 'premium').
        end_date (datetime): Дата окончания подписки.
        is_active (bool): Указывает, является ли подписка активной.
    """

    class Meta:
        model = Subscription
        fields = ["user", "plan", "end_date", "is_active"]
