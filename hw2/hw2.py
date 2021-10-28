from django.core.management import execute_from_command_line
from django.http import HttpResponseRedirect
from django.urls import path
from django.conf import settings
from django.db import connection
from django.shortcuts import render

from random import choice, randrange
from string import ascii_letters, digits
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # Определение пути к файлу

settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    SECRET_KEY='asdf',
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [''],
        }
    ],
    DATABASES={
        'default': {'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / 'data/db.sqlite3'},
    }
)

CREATE_TABLE = '''
CREATE TABLE if not exists url_shortener(
    id integer primary key,
    url_original CHAR(256),
    url_short CHAR(100) 
);
'''


def create_table():
    """
    Создает таблицу из SQL запроса CREATE_TABLE
    """
    with connection.cursor() as cur:
        cur.execute(CREATE_TABLE)


def insert_records(url_orig: str, url_short: str):
    """
    Вставляет передаваемые URL в колонки url_original, url_short
    таблицы url_shortener
    """
    with connection.cursor() as cur:
        query = f'INSERT INTO url_shortener (url_original, url_short) ' \
                f'VALUES(%s, %s)'
        cur.execute(query, (url_orig, url_short))


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
            query = 'SELECT * FROM url_shortener WHERE url_short = %s'
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


def handler(request):
    """
    Функция-обработчик при получении метода POST считывает строку из поля
    url формы файла index.html, проверяет её на допустимые схемы (http,
    https, ftp). При прохождении проверки создаёт короткий URL, записывает его
    вместе с соответствующим оригинальным URL в базу данных и возвращает
    html страничку с короткой ссылкой на оригинальный сайт. Если проверка
    не прошла - выдаёт предупреждение про несоответствие схемы.
    При получении другого метода (GET), выдаёт пустую страничку index.html.
    """
    if request.method == 'POST':
        url_original = request.POST.get('url').lower()
        message = ''
        short_url = ''
        if check_url(url_original):
            url_key = random_url()
            insert_records(url_original, url_key)
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
    Если найден, редиректит на полный URL, сохраненный под данным ключом.
    """
    if find_url(url_key):
        return HttpResponseRedirect(find_url(url_key))
    else:
        return HttpResponseRedirect('/')


urlpatterns = [
    path('', handler),
    path('<url_key>', url_handler)
]

if __name__ == '__main__':
    execute_from_command_line()
    create_table()
