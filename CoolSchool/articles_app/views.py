from django.shortcuts import render, redirect
from .forms import ArticleForm
from datetime import datetime
from .models import Article, Page


# Create your views here.
def index(request):
    return render(request, 'index.html')


def add_main(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.pub_date = datetime.now()
            article.save()
            return redirect('index')
    else:
        form = ArticleForm()
    return render(request, 'edit_page.html', context={'page_name': 'Główna', 'form': form})


def add_news(request):
    return render(request, 'edit_page.html', context={'page_name': 'Aktualności'})


def add_courses(request):
    return render(request, 'edit_page.html', context={'page_name': 'Kursy'})


def add_regulamin(request):
    return render(request, 'edit_page.html', context={'page_name': 'Regulamin'})


def add_privacy_policy(request):
    return render(request, 'edit_page.html', context={'page_name': 'Polityka Prywatności'})


def news(request):
    page = Page.objects.get_or_create(title='news')
    Article.objects.get(page=page)


def courses(request):
    pass


def regulamin(request):
    pass


def privacy_policy(request):
    pass
