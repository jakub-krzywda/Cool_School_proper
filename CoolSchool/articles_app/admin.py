from django.contrib import admin
from .models import Article


# Register your models here.
class MyAdminSite(admin.AdminSite):
    site_header = "Cool School Admin Page"


admin_site = MyAdminSite(name="myadmin")
admin_site.register(Article)