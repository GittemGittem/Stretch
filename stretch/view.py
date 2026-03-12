from .constructors import Stack, Promise, Block

class View: pass

class BlockView(View):
    __slots__ = ("current_line", "lines", "_at", "_block", "line_stack", "init")
    def __init__(self, block:Block, at=None, init=True):
        self._at = at or block
        self._block = block
        self.current_line = 0
        self.lines = Stack([statement for statement in block.stats])
        self.line_stack = Stack()
        self.init = init

    def push(self, line_view):
        self.line_stack.push(line_view)
    def pull(self):
        self.line_stack.pull()
    @property
    def vars(self):
        return self.at.vars
    @property
    def current(self):
        return self.line_stack[0]
    
    def __end__(self):
        return False
    
    def step(self, core):
        if len(self.line_stack) <= 0:
            if self.current_line > len(self.lines) - 1:
                return self.__end__()
            else:
                line = self.lines[self.current_line]
                if line.init == self.init:
                    self.push(LineView(line))
                else:
                    self.current_line += 1
                    return True
            
        line_view = self.line_stack[0]
            
        if not line_view.step(core, self):
            self.pull()
            self.current_line += 1
        return True
    
    @property
    def at(self):
        return self._at
    @property
    def block(self):
        return self._block

class InitView(BlockView):
    def __init__(self, block, at=None):
        super().__init__(block, at, True)
class EnterView(BlockView):
    def __init__(self, block, at=None):
        super().__init__(block, at, False) 

class ForView(EnterView):
    __slots__ = ("current_line", "lines", "_at", "_block", "line_stack", "init", "iter", "var")
    def __init__(self, iterable, var, block, at=None):
        super().__init__(block, at)
        self.iter = Stack(iterable)
        self.var = var
        self.at.vars[self.var] = self.iter.pull()
    def __end__(self):
        if len(self.iter) > 0:
            self.current_line = 0
            self.at.vars[self.var] = self.iter.pull()
            return True
        else:
            return False
        
        


class MultiView:
    def __init__(self, views):
        self.views = views
        self.current = 0
    
    def step(self, core):
        
        if len(self.views) <= 0:
            return False
        
        view_index = self.current % len(self.views)
        view = self.views[view_index]
        if not view.step(core):
            del self.views[view_index]
        
        self.current += 1
        return True
        
        
        

class LineView:
    __slots__ = ("stack", "parts", "promise")
    class Promise(Promise):
        def __init__(self, line_view):
            self.view = line_view
        def load(self):
            return self.view.stack
    def __init__(self, statement=None):
        if statement is None:
            self.parts = Stack()
        else:
            self.parts = Stack(statement.parts)
        self.stack = Stack()
        self.promise = self.Promise(self)
    
    def step(self, core, view):
        if len(self.parts) <= 0:
            return False
        
        core.process(view, self.parts.pop(), self.stack)
        return True
        
        
        
        