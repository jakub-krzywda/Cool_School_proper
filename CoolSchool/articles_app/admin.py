from django.contrib import admin
from .models import Page


# Register your models here.
class MyAdminSite(admin.AdminSite):
    site_header = "Strona Admina Cool School"
    index_template = 'admin/admin.html'

    def index(self, request, extra_content=None):
        pages = list(Page.objects.all())
        titles = [page.title for page in pages]
        urls = [page.page_url for page in pages]
        edit_urls = [page.edit_url for page in pages]
        extra_content = {'combined': zip(titles, urls, edit_urls)}
        return super().index(request, extra_content)


admin_site = MyAdminSite(name="myadmin")
