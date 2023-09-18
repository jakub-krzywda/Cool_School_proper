from django.db import models


class Page(models.Model):
    title = models.CharField(max_length=100)


# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField('date published')
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
