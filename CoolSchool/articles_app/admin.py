from django.contrib import admin
from .models import Article, Page


# Register your models here.
class MyAdminSite(admin.AdminSite):
    site_header = "Strona Admina Cool School"
    index_title = "Poniżej wybierz stronę na którą chcesz dodać artykuł i kliknij dodaj"



admin_site = MyAdminSite(name="myadmin")
admin_site.register(Article)
admin_site.register(Page)

# TODO dodać customowy css i locale
# rosetta