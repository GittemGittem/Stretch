from copy import deepcopy

class Command:
    __slots__ = ("command", "switches")
    def __init__(self, command, *switches):
        self.command = command
        self.switches = frozenset(switches)
    
    def __repr__(self):
        return f"{self.command} {"".join([f'@{switch} ' for switch in self.switches])}->"
    
        
class Statement(list):
    __slots__ = ("parts", "init")
    def __init__(self, *args):
        self.init = False
        super().__init__(*args)
    def __repr__(self):
        return " ".join(repr(part) for part in self) + ";"

class Expression(list):
    def __repr__(self):
        return " ".join(repr(part) for part in self)


class Pair(tuple): pass

class Path:
    __paths__ = {}
    __slots__ = ("path")
    def __new__(cls, *path):
        if path in cls.__paths__:
            return cls.__paths__[path]
        instance = super().__new__(cls)
        instance.path = path
        cls.__paths__[path] = instance
        return instance
    def __init_subclass__(cls):
        cls.__paths__ = {}
    
class Call:
    def __init__(self, obj, args):
        self.obj = obj
        self.args = args
    
    def __iter__(self):
        yield self.obj
        yield self.args
        

class Getitem:
    def __init__(self, obj, key):
        self.obj = obj
        self.key = key

    def __iter__(self):
        yield self.obj
        yield self.key
    
    
class Set(Path):
    def __repr__(self):
        return ".".join(repr(dest) for dest in self.path) + ":"
class Get(Path):
    def __repr__(self):
        return ".".join([repr(dest) for dest in self.path])