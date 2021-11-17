from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView
from blog.models import Post


class CreateUser(CreateView):
    """
    Класс создания нового пользователя. После успешного создания пользователя
    происходит редирект на страницу входа.
    """
    form_class = UserCreationForm
    success_url = reverse_lazy('login_user')
    template_name = 'register.html'


class PostList(ListView):
    """
    Класс со списком всех постов. Используется пагинация и сортировка
    по дате создания.
    """
    model = Post
    template_name = 'home.html'
    paginate_by = 5
    ordering = '-created_at'


class PostAuthorList(ListView):
    """
    Класс со списком постов авторизованного пользователя. Используется пагинация
    и сортировка по дате создания. Фильтрация постов осуществляется путём
    переопределения метода get_queryset.
    """
    model = Post
    template_name = 'home.html'
    paginate_by = 5
    ordering = '-created_at'

    def get_queryset(self):
        queryset = super(PostAuthorList, self).get_queryset()
        queryset = queryset.filter(created_by=self.request.user)
        return queryset


class PostDetail(DetailView):
    """
    Класс отображения поста - отображает всё содержимое поста, с датой создания
    и автором.
    """
    model = Post
    template_name = 'post_detail.html'


class CreatePostView(LoginRequiredMixin, CreateView):
    """
    Класс для создания поста, закрыт авторизацией. Переопределён метод валидации
    формы для заполнения поля created_by именем текущего пользователя.
    """
    model = Post
    fields = ['title', 'text']
    template_name = 'post_new.html'
    login_url = 'login_user'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
    """
    Класс, отвечающий за редактирование страницы поста. Закрыт авторизацией.
    Через переопределение метода dispatch реализована проверка прав
    на редактирование поста (редактировать пост имеет право только автор поста).
    """
    model = Post
    fields = ['title', 'text']
    template_name = 'post_edit.html'
    login_url = 'login_user'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by != self.request.user:
            raise Http404("У вас нет прав редактировать этот пост!")
        return super(PostUpdate, self).dispatch(request, *args, **kwargs)


class PostDelete(LoginRequiredMixin, DeleteView):
    """
    Класс, отвечающий за удаление поста. После завершения удаления записи
    из БД пользователь будет перенаправлен на главную страницу (home)
    с помощью метода reverse_lazy. Закрыт авторизацией. Через переопределение
    метода dispatch реализована проверка прав на удаление поста (удалять пост
    имеет право только автор поста).
    """
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')
    login_url = 'login_user'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by != self.request.user:
            raise Http404("У вас нет прав удалять этот пост!")
        return super(PostDelete, self).dispatch(request, *args, **kwargs)
