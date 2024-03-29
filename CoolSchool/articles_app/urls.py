from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

"""
URL configuration for articles app.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

urlpatterns = [
    path('', views.index, name="index"),
    path('add_article/main/', views.add_main, name="add_main"),
    path('add_article/news/', views.add_news, name="add_news"),
    path('add_article/courses/', views.add_courses, name="add_courses"),
    path('add_article/regulamin/', views.add_regulamin, name="add_regulamin"),
    path('add_article/privacy_policy/', views.add_privacy_policy, name="add_privacy_policy"),
    path('add_article/contact/', views.add_contact, name="add_contact"),
    path('news/', views.news, name="news"),
    path('courses/', views.courses, name="courses"),
    path('regulamin/', views.regulamin, name="regulamin"),
    path('privacy_policy/', views.privacy_policy, name="privacy_policy"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('contact/', views.contact, name='contact'),
    path('edit_article/<int:article_id>/', views.edit_article, name='edit_article'),
    path('delete_article/<int:article_id>/', views.delete_article, name='delete_article'),
]
