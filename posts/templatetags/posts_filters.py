from django import template

register = template.Library()


@register.filter
def is_group(user, group_name):
    """Проверяет, принадлежит ли пользователь к группе."""
    return user.groups.filter(name=group_name).exists()
