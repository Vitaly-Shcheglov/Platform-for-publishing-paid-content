from django.db import models


class Payment(models.Model):
    """
    Модель платежа, связанная с пользователем и постом.

    Эта модель представляет собой платеж, совершенный пользователем за пост или подписку.

    Атрибуты:
        user (ForeignKey): Пользователь, совершивший платеж. Связь с моделью CustomUser.
        payment_date (DateTimeField): Дата и время, когда был совершен платеж.
                                       Автоматически устанавливается при создании платежа.
        paid_post (ForeignKey): Пост, за который был осуществлен платеж.
                                Может быть пустым, если платеж не связан с конкретным постом.
        amount (DecimalField): Сумма платежа в минимальных единицах валюты (например, копейки).
        payment_method (CharField): Метод оплаты. Может принимать значения из PAYMENT_METHODS.
        is_subscription (BooleanField): Указывает, является ли платеж подпиской (True) или одноразовым (False).
        stripe_payment_intent_id (CharField): Уникальный идентификатор платежа в Stripe.
        status (CharField): Статус платежа (например, 'pending', 'succeeded', 'failed').
    """

    PAYMENT_METHODS = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
        ("stripe", "Stripe"),
    ]

    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    paid_post = models.ForeignKey("posts.Post", null=True, blank=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    is_subscription = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default="pending")

    def __str__(self):
        """
        Возвращает строковое представление платежа.

        Возвращает строку с информацией о платеже, включая имя пользователя, сумму и метод платежа.

        Returns:
            str: Информация о платеже, форматированная как "username - amount - payment_method".
        """
        return (
            f"{self.user.username} - {self.amount} - {'Subscription' if self.is_subscription else self.payment_method}"
        )
