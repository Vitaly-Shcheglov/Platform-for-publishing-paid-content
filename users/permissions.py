from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Разрешение для проверки, является ли пользователь модератором.

    Это разрешение используется для ограничения доступа к определенным
    действиям в представлениях на основе принадлежности пользователя
    к группе 'Moderators'.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь разрешение на доступ к представлению.

        Args:
            request (Request): Объект запроса, содержащий информацию о пользователе и запросе.
            view (View): Представление, к которому применяется разрешение.

        Returns:
            bool: True, если пользователь принадлежит группе 'Moderators',
            иначе False.
        """
        return request.user.groups.filter(name="Moderators").exists()
