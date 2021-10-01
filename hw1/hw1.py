from django.core.management import execute_from_command_line
from django.http import HttpResponse
from django.urls import path
from django.conf import settings

import importlib


settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
)


TEMPLATE = """
<!DOCTYPE html>
<html>
 <head>
  <title>{title}</title>
 </head>
 <body>
  <h1>{module_name}</h1>
  {content}
 </body>
</html> 
"""


# def handler(request):
#     # return HttpResponse(TEMPLATE.format(message='Hello, world'))
#     return HttpResponse(TEMPLATE.format(title=title,
#                                         message=choice(quotes)))

def mod_handler(request, mod_name):
    names_in_module = dir(importlib.import_module(mod_name))
    names = [name for name in names_in_module if not name.startswith('_')]
    links = [f'<a href="/doc/{mod_name}/{name}">{name}</a><br>' for name in names]
    # dir(mod_name)
    return HttpResponse(TEMPLATE.format(title=f'Модуль {mod_name}',
                                        module_name=f'Модуль Python {mod_name}',
                                        content=''.join(links)))


def obj_handler(request, mod_name, obj_name):
    doc_txt = f'Описание какой-то функции {obj_name}'
    return HttpResponse(TEMPLATE.format(title=f'Документация модуля {mod_name}',
                                        module_name=f'Документация модуля Python {mod_name}',
                                        content=doc_txt))

urlpatterns = [
    # path('', handler),
    path('doc/<mod_name>', mod_handler),
    path('doc/<mod_name>/<obj_name>', obj_handler),
]

if __name__ == '__main__':
    execute_from_command_line()
