from django.db import models


class Payment(models.Model):
    """
    Модель платежа, связанная с пользователем и курсом.

    Атрибуты:
    - user: пользователь, совершивший платеж.
    - payment_date: дата и время, когда был совершен платеж.
    - paid_post: пост, за который был осуществлен платеж (может быть пустым).
    - amount: сумма платежа.
    - payment_method: метод оплаты (наличные или перевод на счет).
    - is_subscription: поле для покрытия подписки.
    """
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
        ('stripe', 'Stripe'),
    ]

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    paid_post = models.ForeignKey('posts.Post', null=True, blank=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    is_subscription = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        """
        Возвращает строковое представление платежа.

        Returns:
            str: Информация о платеже, включая имя пользователя, сумму и метод платежа.
        """
        return f"{self.user.username} - {self.amount} - {'Subscription' if self.is_subscription else self.payment_method}"
