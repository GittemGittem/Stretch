import importlib
import stretch.builtin_extensions

def get_builtin(path):
    return importlib.import_module(f"stretch.builtin_extensions.{path.dot()}").__extension__