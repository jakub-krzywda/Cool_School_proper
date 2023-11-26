from django.shortcuts import render, redirect
from .forms import ArticleForm
from datetime import datetime
from .models import Article, Page
from django.contrib.auth.decorators import login_required, user_passes_test


def is_superuser(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_superuser)
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


@login_required
@user_passes_test(is_superuser)
def add_news(request):
    return render(request, 'edit_page.html', context={'page_name': 'Aktualności'})


@login_required
@user_passes_test(is_superuser)
def add_courses(request):
    return render(request, 'edit_page.html', context={'page_name': 'Kursy'})


@login_required
@user_passes_test(is_superuser)
def add_regulamin(request):
    return render(request, 'edit_page.html', context={'page_name': 'Regulamin'})


@login_required
@user_passes_test(is_superuser)
def add_privacy_policy(request):
    return render(request, 'edit_page.html', context={'page_name': 'Polityka Prywatności'})


def render_page_based_on_index_template(request, page_name):
    pages = Page.objects.all()
    articles = Article.objects.filter(page__title=page_name)
    default_pages_dict = {}
    for page in pages:
        if page.title not in ('Główna', page_name):
            default_pages_dict.update({page.title: page.page_url.split('/')[0]})
    return render(request, 'index.html', {'default_pages_dict': default_pages_dict, 'current_page_name': page_name, 'articles': articles})


def index(request):
    return render_page_based_on_index_template(request, "Główna")


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
    articles = Article.objects.filter(page__title='Kontakt')
    default_pages_dict = {}
    for page in pages:
        if page.title not in ('Główna', 'Kontakt'):
            default_pages_dict.update({page.title: page.page_url.split('/')[0]})
    return render(request, 'contact.html', {'default_pages_dict': default_pages_dict, 'current_page_name': 'Kontakt',
                                            'articles': articles})
