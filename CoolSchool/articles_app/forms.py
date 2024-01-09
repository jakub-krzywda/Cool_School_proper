from django import forms
from .models import Article
from ckeditor.widgets import CKEditorWidget
from ckeditor.fields import RichTextField


class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Article
        fields = ['title', 'content']