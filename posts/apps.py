from django.apps import AppConfig


class PostsConfig(AppConfig):
    """
    Конфигурация приложения для управления постами.

    Этот класс настраивает параметры приложения 'posts' в Django.
    Он определяет, как приложение будет обрабатываться и какие настройки
    будут применены к нему.

    Атрибуты:
        default_auto_field (str): Тип поля по умолчанию для автоматического увеличения идентификаторов.
        name (str): Имя приложения, которое будет использоваться в Django.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'
