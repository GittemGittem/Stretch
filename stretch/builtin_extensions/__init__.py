import importlib

imported = {}

def __getattr__(extension_name):
    if extension_name in imported:
        extension = imported[extension_name]
    else:
        extension = importlib.import_module("." + extension_name, 'stretch.builtin_extensions')
        imported[extension_name] = extension
    return extension