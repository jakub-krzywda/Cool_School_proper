from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArticleForm
from datetime import datetime
from .models import Article, Page
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


def render_edit_page_based_on_template(request, page_name):
    edit_url = Page.objects.get(title=page_name).edit_url
    articles = list(Article.objects.filter(page__title=page_name))
    articles.sort(key=lambda x: x.pub_date, reverse=True)
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.pub_date = timezone.now()
            article.page = Page.objects.get(title=page_name)
            article.show_on_whiteboard = False
            article.save()
            return redirect(edit_url)
    else:
        form = ArticleForm()
    return render(request, 'edit_page.html', context={'page_name': page_name, 'form': form, 'articles': articles})


def render_page_based_on_index_template(request, page_name):
    pages = Page.objects.all()
    articles = list(Article.objects.filter(page__title=page_name))
    articles.sort(key=lambda x: x.pub_date, reverse=True)
    default_pages_dict = {}
    for page in pages:
        if page.title not in ('Główna', page_name):
            default_pages_dict.update({page.title: page.page_url.split('/')[0]})
    return render(request, 'index.html', {'default_pages_dict': default_pages_dict, 'current_page_name': page_name, 'articles': articles})


@login_required
@user_passes_test(is_superuser)
def add_main(request):
    return render_edit_page_based_on_template(request, 'Główna')


@login_required
@user_passes_test(is_superuser)
def add_news(request):
    page_name = 'Aktualności'
    edit_url = Page.objects.get(title=page_name).edit_url
    articles = list(Article.objects.filter(page__title=page_name))
    articles.sort(key=lambda x: x.pub_date, reverse=True)
    if request.method == 'POST':
        show_on_whiteboard = 'show_on_whiteboard' in request.POST
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.pub_date = timezone.now()
            article.page = Page.objects.get(title=page_name)
            article.show_on_whiteboard = show_on_whiteboard
            article.save()
            return redirect(edit_url)
    else:
        form = ArticleForm()
    return render(request, 'edit_page.html', context={'page_name': page_name, 'form': form, 'articles': articles})


@login_required
@user_passes_test(is_superuser)
def add_courses(request):
    return render_edit_page_based_on_template(request, 'Kursy')


@login_required
@user_passes_test(is_superuser)
def add_regulamin(request):
    return render_edit_page_based_on_template(request, 'Regulamin')


@login_required
@user_passes_test(is_superuser)
def add_privacy_policy(request):
    return render_edit_page_based_on_template(request, 'Polityka Prywatności')


@login_required
@user_passes_test(is_superuser)
def add_contact(request):
    return render_edit_page_based_on_template(request, 'Kontakt')


def index(request):
    page_name = 'Główna'
    pages = Page.objects.all()
    articles = list(Article.objects.filter(page__title=page_name))
    articles.sort(key=lambda x: x.pub_date, reverse=True)
    news_articles = Article.objects.filter(page__title='Aktualności')
    news_articles = list(news_articles.filter(show_on_whiteboard=True))
    news_articles.sort(key=lambda x: x.pub_date, reverse=True)
    default_pages_dict = {}
    for page in pages:
        if page.title not in ('Główna', page_name):
            default_pages_dict.update({page.title: page.page_url.split('/')[0]})
    return render(request, 'index.html', {'default_pages_dict': default_pages_dict, 'current_page_name': page_name, 'articles': articles, 'news_articles': news_articles})


def news(request):
    return render_page_based_on_index_template(request, "Aktualności")


def courses(request):
    return render_page_based_on_index_template(request, "Kursy")


def regulamin(request):
    return render_page_based_on_index_template(request, "Regulamin")


def privacy_policy(request):
    return render_page_based_on_index_template(request, "Polityka Prywatności")


def contact(request):
    pages = Page.objects.all()
    articles = list(Article.objects.filter(page__title='Kontakt'))
    articles.sort(key=lambda x: x.pub_date, reverse=True)
    default_pages_dict = {}
    for page in pages:
        if page.title not in ('Główna', 'Kontakt'):
            default_pages_dict.update({page.title: page.page_url.split('/')[0]})
    return render(request, 'contact.html', {'default_pages_dict': default_pages_dict, 'current_page_name': 'Kontakt',
                                            'articles': articles})


def edit_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    articles = Article.objects.filter(page__title=article.page.title)
    articles = articles.exclude(id=article_id)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            show_on_whiteboard = 'show_on_whiteboard' in request.POST
            article.show_on_whiteboard = show_on_whiteboard
            article.save()
            return redirect(article.page.edit_url)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'edit_article.html', {'form': form, 'article': article, 'articles': articles, 'page_name': article.page.title})


def delete_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    article.delete()
    return redirect(article.page.edit_url)
