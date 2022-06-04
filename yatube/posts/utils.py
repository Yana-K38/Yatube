from django.core.paginator import Paginator

POSTS_ON_THE_PAGE: int = 10


def paginator_page(queryset, request):
    paginator = Paginator(queryset, POSTS_ON_THE_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
