from .constructors import Stack, Array

class BlockView:
    __slots__ = ("current_line", "lines", "_at", "line_stack", "init")
    def __init__(self, block, at=None):
        self._at = at or block
        self.current_line = 0
        self.lines = Array([statement for statement in block.stats])
        self.line_stack = Stack()
        self.init = True

    def push(self, line_view):
        self.line_stack.push(line_view)
    def pull(self):
        self.line_stack.pull()
    
    def step(self, core):
        if len(self.line_stack) <= 0:
            if self.current_line > len(self.lines) - 1:
                if self.init:
                    self.init = False
                    self.current_line = 0
                    return True
                else:
                    return False
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

class LineView:
    __slots__ = ("stack", "parts")
    def __init__(self, statement):
        self.parts = Stack(statement.parts)
        self.stack = Stack()
    
    def step(self, core, view):
        if len(self.parts) <= 0:
            return False
        
        core.process(view, self.parts.pop(), self.stack)
        return True
        
        
        
        