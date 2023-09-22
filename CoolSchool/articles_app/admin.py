from django.contrib import admin
from .models import Article, Page

# Register your models here.
class MyAdminSite(admin.AdminSite):
    site_header = "Strona Admina Cool School"


admin_site = MyAdminSite(name="myadmin")
admin_site.register(Article)
admin_site.register(Page)
admin_site.index_template = 'admin/admin.html'
