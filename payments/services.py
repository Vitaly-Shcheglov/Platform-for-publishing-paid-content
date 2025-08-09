import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def create_product(name, description):
    """
    Создает продукт в Stripe.

    Args:
        name (str): Название продукта.
        description (str): Описание продукта.

    Returns:
        dict: Ответ от Stripe о создании продукта.
    """
    product = stripe.Product.create(
        name=name,
        description=description,
    )
    return product

def create_price(product_id, amount, currency="usd"):
    """
    Создает цену для продукта в Stripe.

    Args:
        product_id (str): ID продукта, для которого создается цена.
        amount (int): Сумма в копейках.
        currency (str): Валюта (по умолчанию 'usd').

    Returns:
        dict: Ответ от Stripe о создании цены.
    """
    price = stripe.Price.create(
        unit_amount=amount,
        currency=currency,
        product=product_id,
    )
    return price

def create_checkout_session(price_id):
    """
    Создает сессию для оплаты в Stripe.

    Args:
        price_id (str): ID цены, соответствующей продукту.

    Returns:
        dict: Ответ от Stripe с URL для оплаты.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:8000/success/",
        cancel_url="http://localhost:8000/cancel/",
    )
    return session

def create_subscription(user, amount):
    """
    Создает разовую подписку для пользователя.

    Args:
        user: Объект пользователя, который будет подписан.
        amount (int): Сумма подписки в копейках.

    Returns:
        dict: Ответ от Stripe с URL для оплаты.
    """

    product = create_product(name="Разовая подписка", description="Оплата за разовую подписку")
    price = create_price(product.id, amount)


    session = create_checkout_session(price.id)
    return session
