from django.contrib import admin
from .models import Post, Category


class CategoryAdmin(admin.ModelAdmin):
    """
    Административная панель для управления категориями.

    Этот класс настраивает отображение категорий в административной панели Django.

    Атрибуты:
        list_display (tuple): Список полей, которые будут отображаться в таблице категорий.
    """
    list_display = ("id", "name")


class PostAdmin(admin.ModelAdmin):
    """
    Административная панель для управления постами.

    Этот класс настраивает отображение постов в административной панели Django
    и позволяет фильтровать и искать посты по определенным полям.

    Атрибуты:
        list_display (tuple): Список полей, которые будут отображаться в таблице постов.
        list_filter (tuple): Список полей, по которым можно фильтровать посты.
        search_fields (tuple): Список полей, по которым можно выполнять поиск.
    """
    list_display = ("id", "title", "category")

    list_filter = ("category",)
    search_fields = ("name", "description")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
