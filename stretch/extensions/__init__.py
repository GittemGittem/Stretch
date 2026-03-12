
import importlib
loaded = {}

def __getattr__(path):
    if path in loaded:
        return loaded[path]
    module = importlib.import_module(f"stretch.extensions.{path}")
    loaded[path] = module
    return module