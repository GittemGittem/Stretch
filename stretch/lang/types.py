
from ..constructors import Group, constructors
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
        
        place.__scope__[final] = value

    def __repr__(self):
        return f"{'.'.join(name for name in self.path)}:"
class Raw(Var):
    def __repr__(self):
        return f"{self.var}?"
class Get:
    __slots__ = ("path")
    def __init__(self, path):
        self.path = tuple(path)
    def get(self, at):
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
        
        return place.__scope__[final]

    def __repr__(self):
        return f"{'.'.join(name for name in self.path)}"
class Constuctor:
    def __init__(self, val):
        self.template = val
    def __repr__(self):
        return f"<- {self.template}"
    def load(self):
        return deepcopy(self.template)
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