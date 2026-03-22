from .structures import Stack

class View:
    
    
    def __init__(self, block):
        self.block = block
        
        self.current_line = 0
        self.parts = Stack()
        self.stack = Stack()
        self.init = False
    
    def __end__(self):
        self.block.get("__scopes__", Stack()).pull_if()
        return False
    
    def next(self, core):
        if len(self.parts) == 0:
            self.stack.clear()
            statements = self.block.get("statements", Stack())
            if self.current_line >= len(statements):
                return self.__end__()
            else:
                statement = statements[self.current_line]
                
                self.current_line += 1
                
                
                if statement.init != self.init:
                    return True
                
                self.parts.extend(statement)
                
        return self.parts.pull(), self.stack
        
    def set(self, path, value):
        final = path[-1]
        path = path[:-1]
        
        __local__ = self.at.get("__local__", self.at)
        
        if len(path) > 0:
            __nonlocal__ = __local__.get("__nonlocal__", __local__)
            start = path[0]
            if start in __local__:
                __scope__ = __local__
            elif start in __nonlocal__:
                __scope__ = __nonlocal__
            
            for dest in path:
                if dest in __scope__:
                    __scope__ = __scope__[dest]
            
            __scope__[final] = value
               
        else:
            __local__[final] = value
        
        
    
    def get(self, path):
        final = path[-1]
        path = path[:-1]
        
        __local__ = self.at.get("__local__", self.at)
        
        __nonlocal__ = __local__.get("__nonlocal__", __local__)
        if len(path) > 0:
            start = path[0]
            if start in __local__:
                __scope__ = __local__
            elif start in __nonlocal__:
                __scope__ = __nonlocal__
            
            for dest in path:
                if dest in __scope__:
                    __scope__ = __scope__[dest]
            
            return __scope__[final]
               
        else:
            if final in __local__:
                return __local__[final]
            else:
                return __nonlocal__[final]
    
    @property
    def at(self):
        return self.block.get("__scopes__", Stack()).peek() or self.block
    
    @property
    def commands(self):
        if "__commands__" in self.block:
            return self.block["__commands__"]
        else:
            from .commands import commands
            return commands