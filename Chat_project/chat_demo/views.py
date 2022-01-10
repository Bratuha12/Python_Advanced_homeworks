from datetime import datetime
import logging
import aiohttp
from aiohttp import web
import aiohttp_jinja2

MAX_USER = 100  # Максимальное количество пользователей чата
admin_dict = {}
archive_dict = {}
log = logging.getLogger(__name__)


def users_lst(request, chat_name: str) -> list:
    """Функция возвращает список пользователей чата"""
    return list(request.app['websockets'][chat_name].keys())


def archive_message(arch_dict: dict, chat_name: str, name: str, message: str,
                    max_length=100) -> dict:
    """
    Функция выполняет добавление сообщений message в словарь arch_dict.
    В словаре сообщения хранятся по ключу (название чата) в виде списка.
    К каждому сообщению добавляется время и имя пользователя, отправившего
    сообщение. Макимальное количество хранимых сообщений ограничено
    параметром max_length, по умолчанию 100 сообщений.
    :param arch_dict: Словарь {chat_name: [message_list]}
    :param chat_name: Название чата.
    :param name: Имя пользователя, отправившего сообщение.
    :param message: Сохраняемое сообщение.
    :param max_length: Максимальное количество сообщений в архиве.
    :return: Словарь {chat_name: [message_list]}
    """
    add_message = f"({datetime.utcnow().strftime('%Z %H:%M:%S')} UTC) {name}: "
    message_list = arch_dict[chat_name]
    message_list.append(add_message + message)
    if len(message_list) > max_length:
        del message_list[0]
    arch_dict.update({chat_name: message_list})
    return arch_dict


async def index(request):
    ws_current = web.WebSocketResponse()  # обертка над текущим веб-сокетом
    ws_ready = ws_current.can_prepare(request)
    # Если полученный объект это не вебсокет, то рендерим шаблон index.html
    if not ws_ready.ok:
        return aiohttp_jinja2.render_template('index.html', request, {})

    # Попытка проапгрейдить HTTP соединение до веб-сокетов
    # (пытаемся открыть web socket)
    await ws_current.prepare(request)

    # Из вебсокета получаем json-данные, откуда извлекаем
    # имя подключившегося пользователя (name) и название чата (chat)
    conn_data = await ws_current.receive_json()
    name = conn_data['user']
    chat = conn_data['chat_name']

    # Проверка длины имени чата (строка от 3 до 8 символов)
    if len(chat) not in range(3, 9):
        # Используем логирование (вывод в терминал) в любом месте кода
        log.info(f'The length of the chat name ({chat}) '
                 f'must be between 3 and 8 characters.')
        await ws_current.send_json(
            {'action': 'interrupt', 'name': name, 'chat': chat,
             'message': f'The length of the chat name ({chat}) '
                        f'must be between 3 and 8 characters.'
             })
        return ws_current

    chat_dict = request.app['websockets'].get(chat)
    if chat_dict:
        # Перед подключением нового пользователя проводим проверку
        # на максимальное число пользователей чата
        if len(chat_dict) > MAX_USER - 1:
            log.info(
                f'Количество пользователей чата {chat} превысило {MAX_USER}.')
            await ws_current.send_json(
                {'action': 'interrupt', 'name': name, 'chat': chat,
                 'message': f'The number of chat users ({chat}) '
                            f'has exceeded {MAX_USER}.',
                 })
            return ws_current
        # Перед подключением нового пользователя проводим проверку
        # на уникальность его имени в чате
        elif name in chat_dict.keys():
            log.info('%s уже существует.', name)
            await ws_current.send_json(
                {'action': 'interrupt', 'name': name, 'chat': chat,
                 'message': f'{name} already exists!'
                 })
            return ws_current
        else:
            # Подключившихся пользователей будем хранить в объекте Application,
            # доступ к которому получаем через request.app['websockets'].
            # Помещаем имя пользователя и его websocket в словарь
            # подключившихся пользователей данного чата.
            request.app['websockets'][chat][name] = ws_current
    else:
        # Если чата с указанным именем не существует - создаём новый словарь
        # с ключём-именем нового чата
        request.app['websockets'].update({chat: {name: ws_current}})
        # 1й пользователь чата становится админом чата,
        # сохранем его в словаре админов.
        admin_dict.update({chat: name})
        archive_dict.update({chat: []})

    log.info(f'{name} joined.')

    # Из архивного списка сообщений чата создаём его строковое представление
    archive_str = '<br>'.join(archive_dict[chat])
    # Отправляем на клиент JSON-данные, которые клиент извлечёт и обработает
    # с помощью javascript
    await ws_current.send_json(
        {'action': 'connect', 'name': name, 'chat': chat,
         'admin': admin_dict[chat], 'archive': archive_str})

    # Список пользователей чата
    chat_users = users_lst(request, chat)

    # Оповещаем всех, что новый пользователь присоединился
    for ws in request.app['websockets'][chat].values():
        await ws.send_json(
            {'action': 'join', 'name': name, 'chat_users': chat_users})

    # Цикл, в котором пользователь отправляет сообщения в чат,
    # в который он подключён
    while True:
        msg = await ws_current.receive()

        try:
            # Реализация функции удаления пользователя админом (kick)
            chat = msg.json()['chat_name']
            user = msg.json()['user']
            kick_user = msg.json()['kick_user']
            if user == admin_dict[chat]:
                del request.app['websockets'][chat][kick_user]
        except:

            # Если текущий вебсокет не в словаре чата, то значит пользователь
            # удалён из чата админом - прерываем его сессию.
            if ws_current not in request.app['websockets'][chat].values():
                await ws_current.send_json(
                    {'action': 'interrupt', 'name': name, 'chat': chat,
                     'message': f'Admin ({admin_dict[chat]}) kick you!'
                     })
                chat_users = users_lst(request, chat)
                for ws in request.app['websockets'][chat].values():
                    await ws.send_json(
                        {'action': 'disconnect', 'name': name,
                         'chat_users': chat_users})
            # Проверяем тип сообщения, если текст, то отправляем его
            # всем пользователям в комнате
            elif msg.type == aiohttp.WSMsgType.text:
                archive_message(archive_dict, chat, name, msg.data)
                for ws in request.app['websockets'][chat].values():
                    if ws is not ws_current:
                        await ws.send_json(
                            {'action': 'sent', 'name': name, 'text': msg.data})
            else:
                break  # Производим дисконнект

    # После отключения пользователя, удаляем его имя из словаря 'websockets',
    # если он был последним в чате, то удаляется словарь чата и удаляем админа
    # этого чата из словаря админов.
    if len(request.app['websockets'][chat]) > 1:
        del request.app['websockets'][chat][name]
        log.info('%s disconnected.', name)
        chat_users = users_lst(request, chat)
        # Оповещаем всех, что пользователь вышел
        for ws in request.app['websockets'][chat].values():
            await ws.send_json({'action': 'disconnect', 'name': name,
                                'chat_users': chat_users})
    else:
        del request.app['websockets'][chat]
        del admin_dict[chat]

    return ws_current
