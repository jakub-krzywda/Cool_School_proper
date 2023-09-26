from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'index.html')


def add_main(request):
    return render(request, 'edit_page.html', context={'page_name': 'Główna'})


def add_news(request):
    return render(request, 'edit_page.html', context={'page_name': 'Aktualności'})


def add_courses(request):
    return render(request, 'edit_page.html', context={'page_name': 'Kursy'})


def add_regulamin(request):
    return render(request, 'edit_page.html', context={'page_name': 'Regulamin'})


def add_privacy_policy(request):
    return render(request, 'edit_page.html', context={'page_name': 'Polityka Prywatności'})
