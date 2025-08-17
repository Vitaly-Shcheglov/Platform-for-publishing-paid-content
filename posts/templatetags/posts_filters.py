from django import template

register = template.Library()


@register.filter
def is_group(user, group_name):
    """
    Проверяет, принадлежит ли пользователь к указанной группе.

    Этот фильтр можно использовать в шаблонах Django для проверки,
    является ли данный пользователь членом группы с заданным именем.

    Args:
        user (User): Объект пользователя, который необходимо проверить.
        group_name (str): Название группы, к которой нужно проверить принадлежность пользователя.

    Returns:
        bool: Возвращает True, если пользователь принадлежит к указанной группе;
              в противном случае возвращает False.
    """
    return user.groups.filter(name=group_name).exists()
