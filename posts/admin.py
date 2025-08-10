from django.contrib import admin
from .models import Post, Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category")

    list_filter = ("category",)
    search_fields = ("name", "description")


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
