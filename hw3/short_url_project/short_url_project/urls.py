"""short_url_project URL Configuration

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
from shortener.views import handler, url_handler, create_user, logout_user, \
    start
import django.contrib.auth.views as auth_views

urlpatterns = [
    path('admin12/', admin.site.urls),
    path('register/', create_user),
    path('accounts/login',
         auth_views.LoginView.as_view(template_name='login.html')),
    path('logout', logout_user),
    path('shortener', handler),
    path('<url_key>', url_handler),
    path('', start),
]
