
from ..constructors import Group, Array, constructors



class Var:
    __slots__ = ("var",)
    __names__ = {}
    def __new__(cls, name):
        if name in cls.__names__:
            return cls.__names__[name]
        else:
            var = super().__new__(cls)
            cls.__names__[name] = var
            return var
    def __init_subclass__(cls):
        cls.__names__ = dict()
    def __init__(self, name):
        self.var = name  
class Set(Var):
    def set(self, at, value):
        at.__scope__[self.var] = value
    def __repr__(self):
        return f"{self.var}:"
class Get(Var):
    __slots__ = ("var")
    def get(self, at):
        return at.__scope__[self.var]
    def __repr__(self):
        return f"{self.var}"
class Constuctor(Var):
    def __repr__(self):
        return f"<- {self.var}"
    def load(self):
        return constructors[self.var]()
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