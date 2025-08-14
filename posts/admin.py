from django.contrib import admin

from .models import Category, Subcategory, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Административная панель для управления категориями.

    Этот класс настраивает отображение категорий в административной панели Django.

    Атрибуты:
        list_display (tuple): Список полей, которые будут отображаться в таблице категорий.
    """

    list_display = ("id", "name")


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Subcategory.

    Этот класс управляет отображением и функциональностью модели Subcategory
    в административной панели Django. Он наследуется от admin.ModelAdmin
    и позволяет настраивать, как модель будет представлена и управляться.

    Атрибуты:
        list_display (tuple): Кортеж, определяющий, какие поля модели
            будут отображаться в списке объектов в административной панели.
            В данном случае отображаются 'id' и 'name'.
        search_fields (tuple): Список полей, по которым можно выполнять поиск.

    Методы:
        - list_display: Определяет, какие поля будут отображены в таблице списка
            объектов. В этом случае отображаются идентификатор и название подкатегории.
        - search_fields: Определяет, по каким полям можно выполнять поиск в
            административной панели. В данном случае поиск осуществляется по
            названию подкатегории, что упрощает поиск нужных элементов.
    """

    list_display = ('id', 'name', 'category')
    search_fields = ('name',)


@admin.register(Post)
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

    list_display = ("id", "title", "category", "is_published", "created_at")

    list_filter = ("category", "is_published")
    search_fields = ("title", "content")
