"""blog_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from blog.views import post_detail, create_user, post_list, post_author_list, \
    create_post_view, post_update, post_delete
import django.contrib.auth.views as auth_views


urlpatterns = [
    path('admin12/', admin.site.urls),
    path('register/', create_user, name='register_user'),
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='login.html'),
         name='login_user'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'),
         name='logout_user'),
    path('', post_list, name='home'),
    path('post/new/', create_post_view, name='post_new'),
    path('post/<int:pk>/', post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', post_update, name='post_edit'),
    path('post/<int:pk>/delete/', post_delete, name='post_delete'),
    path('post/author_posts/', post_author_list, name='post_author_list'),
]
