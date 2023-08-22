from rest_framework.pagination import PageNumberPagination


class RestrictPagination(PageNumberPagination):
    page_size_query_param = 'limit'
