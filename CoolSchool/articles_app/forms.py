from django import forms
from .models import Article
from ckeditor.widgets import CKEditorWidget


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']
        labels = {
            'title': 'Tytuł',
            'content': 'Treść'
        }
        widgets = {
            'content': CKEditorWidget(),
        }
