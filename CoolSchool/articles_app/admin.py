from django.contrib import admin
from .models import Page, Article
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


class MyAdminSite(admin.AdminSite):
    site_header = "Strona Admina Cool School"
    index_template = 'admin/admin.html'

    @method_decorator(never_cache)
    def index(self, request):
        pages = list(Page.objects.all())
        titles = [page.title for page in pages]
        urls = [page.page_url for page in pages]
        edit_urls = [page.edit_url for page in pages]
        extra_content = {'combined': zip(titles, urls, edit_urls)}
        return super().index(request, extra_content)


admin_site = MyAdminSite(name="myadmin")
admin_site.register(Article)
admin_site.register(Page)