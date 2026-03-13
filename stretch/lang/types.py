
from ..constructors import Group
from copy import deepcopy


class Var:
    __slots__ = ("var",)
    __names__ = {}
    def __new__(cls, name):
        if isinstance(name, Var):
            return name
        if name in cls.__names__:
            return cls.__names__[name]
        else:
            var = super().__new__(cls)
            var.var = name
            cls.__names__[name] = var
            return var
    def __deepcopy__(self, memo):
        return self
    def __init_subclass__(cls):
        cls.__names__ = dict()
class Set:
    __slots__ = ("path")
    def __init__(self, path):
        self.path = tuple(path)
    def set(self, at, value):
        final = self.path[-1]
        path = self.path[:-1]
        place = at
        for dest in path:
            if hasattr(place, "__scope__"):
                where = place.__scope__
            if dest in where:
                place = where[dest]
            else:
                raise Exception()
        
        place[final] = value

    def __repr__(self):
        return f"{'.'.join(name for name in self.path)}:"
class Get:
    __slots__ = ("path")
    def __init__(self, path):
        self.path = tuple(path)
    def get(self, at):
        final = self.path[-1]
        path = self.path[:-1]
        place = at
        for dest in path:
            if dest in place:
                place = place[dest]
            else:
                raise Exception()
        
        return place[final]

    def __repr__(self):
        return f"{'.'.join(name for name in self.path)}"
class Call:
    def __init__(self, args):
        self.args = args
    def __call__(self, core, stack, obj):
        from ..view import EnterView
        bl = obj.get("__call__", None)
        params = obj.get("params", Group())
        print(self.args)
        if len(params) != len(self.args):
            raise Exception()
        if bl is None:
            raise Exception()
        for index, param in enumerate(params):
            bl[param] = self.args[index]
        
        core.interpreter.push(EnterView(bl))
        stack.push(bl["promise"])

class GetItem:
    def __init__(self, key):
        self.key = key
        
    def __call__(self, core, stack, obj):
        stack.push(obj[self.key])
class Operator(Var):

    def __repr__(self):
        return self.var

class Expression(list):
    def __repr__(self):
        return f"{' '.join([str(term) for term in self])}"
class ParExpression(Expression):
    def __repr__(self):
        return f"({super().__repr__()})"

class Command:
    __slots__ = ("command", "switches")
    def __init__(self, command, switches):
        self.command = command
        self.switches = tuple(switches)
        
    def __repr__(self):
        return f"{self.command} {"".join([f'@{switch} ' for switch in self.switches])}->"