from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.db import connection
from random import choice, randrange
from string import ascii_letters, digits
from shortener.models import UrlShortener

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


def find_url(url_key: str):
    """
    Функция ищет ключ (случайная последовательность символов после адреса хоста)
    короткого URL в таблице url_shortener и возвращает соответствующий ему
    оригинальный URL или значение False при ненахождении объекта поиска.
    :param url_key: Искомый ключ короткого URL.
    :return: Оригинальный URL или значение False.
    """
    try:
        with connection.cursor() as cur:
            query = 'SELECT * FROM shortener_urlshortener WHERE url_short = %s'
            cur.execute(query, [url_key])
            record = cur.fetchone()
        return record[1]
    except:
        return False


def check_url(url_txt: str) -> bool:
    """
    Функция проверяет URL. Допускаются следующие схемы: http, https, ftp.
    Если URL прошел проверку, возвращает True, иначе - False.
    :param url_txt: Проверяемый URL
    :return: True или False
    """
    return url_txt.startswith(('http://', 'https://', 'ftp://'))


def random_url(min_=5, max_=8) -> str:
    """
    Функция генерирует случайную последовательность цифр и букв.
    Минимальная длина ключа - min_ символов, максимальная - max_ символов.
    Также производится проверка сгенерированной последовательности
    на уникальность - через поиск в базе данных, с использованием рекурсии.
    :param: min_: Минимальная длина случайной последовательности.
            max_: Максимальная длина случайной последовательности.
    :return: Случайная последовательность букв и цифр.
    """
    dictionary = ascii_letters + digits
    pass_length = randrange(min_, max_)
    random_str = ''.join(choice(dictionary) for _ in range(pass_length))
    if find_url(random_str):
        return random_url(min_, max_)
    else:
        return random_str


@login_required(login_url='login_user')
def handler(request):
    """
    Функция-обработчик при получении метода POST считывает строку из поля
    url формы файла index.html, проверяет её на допустимые схемы (http,
    https, ftp). При прохождении проверки создаёт короткий URL, записывает его
    вместе с соответствующим оригинальным URL и ссылкой на пользователя,
    добавившего эту ссылку, в базу данных, затем возвращает html страничку
    с короткой ссылкой на оригинальный сайт. Если проверка не прошла - выдаёт
    предупреждение про несоответствие схемы.
    При получении другого метода (GET), выдаёт пустую страничку index.html.
    Функция доступна только аутентифицированным пользователям. Если пользователь
    не авторизирован, происходит переадресация на страницу авторизации.
    """
    if request.method == 'POST':
        url_original = request.POST.get('url').lower()
        message = ''
        short_url = ''
        if check_url(url_original):
            url_key = random_url()
            user_auth = request.user
            u = UrlShortener(url_original=url_original, url_short=url_key,
                             user=user_auth)
            u.save()
            short_url = ''.join(('http://', request.get_host(), '/', url_key))
        else:
            message = 'Ваш URL не прошел проверку. Допускаются следующие ' \
                      'схемы: http, https, ftp.'
        return render(request, 'index.html', {'message': message,
                                              'current_url': url_original,
                                              'short_url': short_url})
    else:
        return render(request, 'index.html')


def url_handler(request, url_key):
    """
    Функция-обработчик, которая при переходе по ссылке с ключом вида
    http://localhost:8000/<url_key> ищет ключ в базе. Если ключ не найден,
    перенаправляет (производит HTTP редирект) на главную страницу.
    Если найден, редиректит на полный URL, сохраненный под данным ключом,
    а также увеличивает счётчик редиректов redirect_count на 1.
    """
    if find_url(url_key):
        u = UrlShortener.objects.get(url_short=url_key)
        u.redirect_count += 1
        u.save()
        return HttpResponseRedirect(find_url(url_key))
    else:
        return HttpResponseRedirect('/')


def start(request):
    """
    Функция-обработчик, которая производит проверку аутентификации пользователя.
    Если проверка пройдена, то перенаправляет на страницу сервиса для сокращения
    ссылок. Если нет - отображается стартовая страница с ссылками на Логин и
    Регистрацию пользователя.
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect('shortener')
    else:
        return render(request, 'start.html')
