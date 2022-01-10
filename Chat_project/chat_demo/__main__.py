import logging
from aiohttp import web
import jinja2  # пакет для рендера шаблонов
import aiohttp_jinja2  # асинхронная обертка на jinja2

from chat_demo import views


# Главный объект aiohttp (совокупность сеттингов и роутеров)
async def init_app():
    # Инициализация объекта Application, точка входа в aiohttp приложение
    app = web.Application()
    # В экземпляре объекта Application создаём словарь с ключём 'websockets',
    # в котором будут хранится подключившиеся пользователи в виде
    # словаря {chat_name: {name: ws_current}}, где chat_name - название чата,
    # name - имя пользователя, ws_current - экземпляр web socket.
    app['websockets'] = {}
    # Конфигурация темплейтов, инициализация пакета aiohttp_jinja2,
    # где 'chat_demo' - это имя пакета, а 'templates' - имя каталога с шаблонами
    aiohttp_jinja2.setup(app,
                         loader=jinja2.PackageLoader('chat_demo', 'templates'))
    app.router.add_get('/', views.index)  # роутер для главной страницы-хэндлер
    return app


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = init_app()
    web.run_app(app)  # стартуем aiohttp сервер (полноценный сервер для работы)


if __name__ == '__main__':
    main()
