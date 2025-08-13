from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """
    Конфигурация приложения для управления платежами.

    Этот класс настраивает параметры приложения 'payments' в Django.

    Атрибуты:
        default_auto_field (str): Тип поля по умолчанию для автоматического увеличения идентификаторов.
        name (str): Имя приложения, которое будет использоваться в Django.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
