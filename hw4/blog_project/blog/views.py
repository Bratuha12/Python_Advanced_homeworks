from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.db import models


# Create your views here.
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from blog.models import Post


def create_user(request):
    """
    Функция создаёт нового пользователя с помощью формы для регистрации.
    Если форма для регистрации заполнена и проверена, сохраняет нового
    пользователя в базу данных auth_user с правами персонала (атрибут is_staff)
    и редиректит на главную страницу.
    """
    form = UserCreationForm(request.POST or None)
    if form.is_bound and form.is_valid():
        user = form.save()
        user.is_staff = True
        user.save()
        return redirect('/')
    return render(request, 'register.html', {'form': form})


def logout_user(request):
    """
    Функция производит логаут пользователя и редиректит на главную страницу.
    """
    logout(request)
    return redirect('/')


class PostList(ListView):
    """
    Класс страницы со списком всех постов. Используется пагинация и сортировка
    по дате создания.
    """
    model = Post
    template_name = 'home.html'
    paginate_by = 5
    ordering = '-created_at'


class PostDetail(DetailView):
    """
    Класс страницы поста отображает всё содержимое поста, с датой создания и
    автором.
    """
    model = Post
    template_name = 'post_detail.html'
    # template_name = 'post.html'


class CreatePostView(LoginRequiredMixin, CreateView):
    """
    Класс для создания поста, закрыт авторизацией. Переопределён метод валидации
    формы для заполнения поля created_by именем текущего пользователя.
    """
    model = Post
    fields = ['title', 'text']
    template_name = 'post_new.html'
    # template_name = 'new_post.html'
    success_url = '/'
    login_url = '/accounts/login'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class PostUpdate(UpdateView):
    """
    Класс страницы редактирования поста.
    """
    model = Post
    fields = ['title', 'text']
    template_name = 'post_edit.html'
