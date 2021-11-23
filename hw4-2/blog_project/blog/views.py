from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404

from blog.forms import PostForm
from blog.models import Post


# class CreateUser(CreateView):
#     """
#     Класс создания нового пользователя. После успешного создания пользователя
#     происходит редирект на страницу входа.
#     """
#     form_class = UserCreationForm
#     success_url = reverse_lazy('login_user')
#     template_name = 'register.html'

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
        return redirect('login_user')
    return render(request, 'register.html', {'form': form})


# class PostList(ListView):
#     """
#     Класс со списком всех постов. Используется пагинация и сортировка
#     по дате создания.
#     """
#     model = Post
#     template_name = 'home.html'
#     paginate_by = 5
#     ordering = '-created_at'

def post_list(request):
    queryset = Post.objects.all().order_by('-created_at')
    paginator = Paginator(queryset, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'home.html', context)


# class PostAuthorList(ListView):
#     """
#     Класс со списком постов авторизованного пользователя. Используется пагинация
#     и сортировка по дате создания. Фильтрация постов осуществляется путём
#     переопределения метода get_queryset.
#     """
#     model = Post
#     template_name = 'home.html'
#     paginate_by = 5
#     ordering = '-created_at'
#
#     def get_queryset(self):
#         queryset = super(PostAuthorList, self).get_queryset()
#         queryset = queryset.filter(created_by=self.request.user)
#         return queryset

def post_author_list(request):
    queryset = Post.objects.filter(created_by=request.user).order_by(
        '-created_at')
    paginator = Paginator(queryset, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'home.html', context)


# class PostDetail(DetailView):
#     """
#     Класс отображения поста - отображает всё содержимое поста, с датой создания
#     и автором.
#     """
#     model = Post
#     template_name = 'post_detail.html'

def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    context = {'object': post}
    return render(request, 'post_detail.html', context)


# class CreatePostView(LoginRequiredMixin, CreateView):
#     """
#     Класс для создания поста, закрыт авторизацией. Переопределён метод валидации
#     формы для заполнения поля created_by именем текущего пользователя.
#     """
#     model = Post
#     fields = ['title', 'text']
#     template_name = 'post_new.html'
#     login_url = 'login_user'
#
#     def form_valid(self, form):
#         form.instance.created_by = self.request.user
#         return super().form_valid(form)

@login_required(login_url='login_user')
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.instance.created_by = request.user
            post = form.save()
            return redirect('post_detail', post.pk)
    else:
        form = PostForm()
    return render(request, 'post_new.html', {'form': form})


# class PostUpdate(LoginRequiredMixin, UpdateView):
#     """
#     Класс, отвечающий за редактирование страницы поста. Закрыт авторизацией.
#     Через переопределение метода dispatch реализована проверка прав
#     на редактирование поста (редактировать пост имеет право только автор поста).
#     """
#     model = Post
#     fields = ['title', 'text']
#     template_name = 'post_edit.html'
#     login_url = 'login_user'
#
#     def dispatch(self, request, *args, **kwargs):
#         obj = self.get_object()
#         if obj.created_by != self.request.user:
#             raise Http404("У вас нет прав редактировать этот пост!")
#         return super(PostUpdate, self).dispatch(request, *args, **kwargs)

@login_required(login_url='login_user')
def post_update(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post.created_by != request.user:
        raise Http404("У вас нет прав редактировать этот пост!")
    if request.POST:
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk)
    form = PostForm(instance=post)
    context = {'form': form}
    return render(request, 'post_edit.html', context)


# class PostDelete(LoginRequiredMixin, DeleteView):
#     """
#     Класс, отвечающий за удаление поста. После завершения удаления записи
#     из БД пользователь будет перенаправлен на главную страницу (home)
#     с помощью метода reverse_lazy. Закрыт авторизацией. Через переопределение
#     метода dispatch реализована проверка прав на удаление поста (удалять пост
#     имеет право только автор поста).
#     """
#     model = Post
#     template_name = 'post_delete.html'
#     success_url = reverse_lazy('home')
#     login_url = 'login_user'
#
#     def dispatch(self, request, *args, **kwargs):
#         obj = self.get_object()
#         if obj.created_by != self.request.user:
#             raise Http404("У вас нет прав удалять этот пост!")
#         return super(PostDelete, self).dispatch(request, *args, **kwargs)

@login_required(login_url='login_user')
def post_delete(request, pk):
    post = get_object_or_404(Post, id=pk)
    if post.created_by != request.user:
        raise Http404("У вас нет прав редактировать этот пост!")
    if request.POST:
        post.delete()
        return redirect('home')
    form = PostForm(instance=post)
    context = {'form': form, 'object': post}
    return render(request, 'post_delete.html', context)
