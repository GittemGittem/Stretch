import importlib
from stretch.core_types import StretchTerminate
imported = {}

def __getattr__(extension_name):
    if extension_name in imported:
        extension = imported[extension_name]
    else:
        try:
            extension = importlib.import_module("." + extension_name, 'stretch.builtin_extensions')
        except:
            raise StretchTerminate(f"Stretch builtin extensions does not contain '{extension_name}'")
        imported[extension_name] = extension
    return extension

