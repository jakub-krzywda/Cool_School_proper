from django.contrib import admin


# Register your models here.
class MyAdminSite(admin.AdminSite):
    site_header = "Cool School Admin Page"


admin_site = MyAdminSite(name="myadmin")

