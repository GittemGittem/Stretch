from garnish import garnish
from copy import deepcopy
from .commands import commands
from .operators import operators, precedence
constructors = {}

@garnish
def new(cls, name):
    global constructors
    constructors[name] = cls
    return cls

class Promise: pass


@new.use("group") 
class Group(tuple):
    def __repr__(self):
        return f"({", ".join(str(value) for value in self)})"
    def dot(self):
        return ".".join(self)


@new.use("stack")
class Stack(list):
    def push(self, value):
        list.insert(self, 0, value)
    def pull(self, index=0):
        return self.pop(0)
    def peek(self, index=0):
        if index < len(self):  
            return self[index]
        return None
    def peek_if(self, type, index=0):
        if index < len(self):
            if isinstance(self.peek(index), type): 
                return self[index]
        return None
    def pull_if(self, type):
        if len(self) > 0:
            if isinstance(self[0], type):
                return self.pull()
        return None
    def pull_only(self, type):
        if len(self) > 0:
            if isinstance(self[0], type):
                return self.pull()
        raise TypeError()
    
    def insert(self, value, index=0):
        list.insert(self, index, value)
        
    def __repr__(self):
        return f"[{", ".join([str(item) for item in self])}]"
    dot = Group.dot


@new.use("block")
class Block:
    __slots__ = (
        "stats",
        "__scope__",
        "promise",
        
        "commands",
        "constructors",
        "operators",
        "precedence"
        )
    class Promise(Promise):
        __slots__ = ("return_stack", "block")
        def __init__(self, block):
            self.return_stack = Stack()
            self.block = block
        def load(self):
            if len(self.return_stack) > 0:
                return self.return_stack.pull()
            else:
                return self.block
        
    def __init__(self, statements=None):
        self.stats = statements or []
        self.__scope__ = {}
        self.promise = self.Promise(self)
        
        self.commands = deepcopy(commands)
        self.constructors = deepcopy(constructors)
        self.operators = deepcopy(operators)
        self.precedence = deepcopy(precedence)
    
    @property
    def vars(self):
        return self.__scope__
        
    def __repr__(self, nested = 1):
        return f"{{\n{"\n".join(f'    {str(stat)}' for stat in self.stats)}\n}}"

class Statement:
    __slots__ = ("parts", "init")
    def __init__(self, statement = [], init=False):
        self.parts = statement
        self.init = init
    def __repr__(self):
        return f"{" ".join(str(part) if not isinstance(part, str) else f'"{part}"' for part in self.parts)};"