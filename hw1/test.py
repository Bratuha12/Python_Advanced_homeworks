import importlib
module_name = 'math'
importlib.import_module(module_name)


print(dir(importlib.import_module('math')))

