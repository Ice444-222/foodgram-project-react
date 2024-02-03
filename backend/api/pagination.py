from rest_framework.pagination import PageNumberPagination


class UserPageNumberPagination(PageNumberPagination):
    """
    Стандартный класс пагинатора, который ограничивает
    количество объектов на странице.
    """

    page_size_query_param = 'limit'
    page_size = 5
