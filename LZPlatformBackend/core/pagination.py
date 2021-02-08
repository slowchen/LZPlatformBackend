from rest_framework.pagination import PageNumberPagination

from ..core.response import APIResponse


class DefaultPageNumberPagination(PageNumberPagination):
    """
    分页类，配置在 settings.py-REST_FRAMEWORK-DEFAULT_PAGINATION_CLASS和PAGE_SIZE
    """
    # page_size = 1
    max_page_size = 100
    page_size_query_param = 'page_size'
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return APIResponse(data=data, next=self.get_next_link(),
                           previous=self.get_previous_link(), total=self.page.paginator.count)
