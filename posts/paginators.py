from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Кастомный класс пагинации для управления количеством элементов на странице.
    """

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100
