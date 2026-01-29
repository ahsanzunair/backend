from rest_framework.pagination import PageNumberPagination

class JobPagination(PageNumberPagination):
    """Custom pagination for jobs"""
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100