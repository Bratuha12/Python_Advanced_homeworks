from django.core.management import execute_from_command_line
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import path
from django.conf import settings

import importlib

settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    SECRET_KEY='asd',
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


def mod_handler(request, mod_name):
    try:
        names_in_module = dir(importlib.import_module(mod_name))
        names = [name for name in names_in_module if not name.startswith('_')]
        links = [f'<a href="/doc/{mod_name}/{name}">{name}</a><br>' for name in
                 names]
        return HttpResponse(TEMPLATE.format(title=f'Модуль {mod_name}',
                                            module_name=f'Модуль Python {mod_name}',
                                            content=''.join(links)))
    except ModuleNotFoundError:
        return HttpResponseNotFound()


def obj_handler(request, mod_name, obj_name):
    try:
        module = importlib.import_module(mod_name)
        obj_doc = getattr(module, obj_name).__doc__
        return HttpResponse(obj_doc, content_type='text/plain')
    except (ModuleNotFoundError, AttributeError):
        return HttpResponseNotFound()


urlpatterns = [
    path('doc/<mod_name>', mod_handler),
    path('doc/<mod_name>/<obj_name>', obj_handler),
]

if __name__ == '__main__':
    execute_from_command_line()
