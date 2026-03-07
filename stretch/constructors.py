from garnish import garnish
from .commands import commands
from .operators import operators, precedence
constructors = {}

@garnish
def new(cls, name):
    global constructors
    constructors[name] = cls
    return cls


class Statement:
    __slots__ = ("parts", "init")
    def __init__(self, statement = [], init=False):
        self.parts = statement
        self.init = init
    def __repr__(self):
        return f"{" ".join(str(part) for part in self.parts)};"

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
        return f"{{{", ".join([str(item) for item in self])}}}"

@new.use("group") 
class Group(tuple):
    def __repr__(self):
        return f"({", ".join(str(value) for value in self)})"
class Cluster(tuple):
    def __repr__(self):
        return f"<{".".join(str(value) for value in self)}>"

@new.use("array")
class Array(list): pass

@new.use("dict")
class Dictionary(dict): pass

@new.use("block")
class Block:
    __slots__ = (
        "stats",
        "__scope__",
        "promise",
        
        "__commands__",
        "__constructors__",
        "__operators__",
        "__precedence__"
        )
    class Promise:
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
        self.stats = statements or Array()
        self.__scope__ = Dictionary()
        self.promise = self.Promise(self)
        
        self.__commands__ = None
        self.__constructors__ = None
        self.__operators__ = None
        self.__precedence__ = None
    
    @property
    def commands(self):
        return self.__commands__ or commands
    @property
    def constuctors(self):
        return self.__constructors__ or constructors
    @property
    def operators(self):
        return self.__operators__ or operators
    @property
    def precedence(self):
        return self.__precedence__ or precedence
        
    def __repr__(self, nested = 1):
        return f"{{\n{"\n".join(f'    {str(stat)}' for stat in self.stats)}\n}}"
