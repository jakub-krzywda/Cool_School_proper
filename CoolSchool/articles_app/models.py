from django.db import models
from ckeditor.fields import RichTextField

class Page(models.Model):
    title = models.CharField(max_length=100)
    page_url = models.URLField(max_length=200, blank=True, null=True)
    edit_url = models.URLField(max_length=200, blank=True, null=True)


# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()
    pub_date = models.DateTimeField('date published')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
