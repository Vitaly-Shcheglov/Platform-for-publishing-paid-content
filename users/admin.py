from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class AutorAdmin(admin.ModelAdmin):
    """
    Административная панель для управления пользователями.

    Этот класс настраивает отображение модели CustomUser в административной панели Django.
    Он исключает поле 'password' из формы редактирования, чтобы защитить конфиденциальность паролей.

    Атрибуты:
        exclude (tuple): Поля, которые будут исключены из формы редактирования в админ-панели.
    """

    exclude = ("password",)
