
from .constructors import Stack
from .parser import parse

class Interpreter:
    def __init__(self):
        self.view_stack = Stack()
        self.try_stack = Stack()
        self.running = False
    
    @staticmethod
    def parse(code):
        return parse(code)
    
    def push(self, view):
        self.view_stack.push(view)
    def pull(self):
        return self.view_stack.pull()
    
    def mainloop(self, core):
        self.running = True

        while self.running:
            if len(self.view_stack) > 2000:
                raise RecursionError()
            if len(self.view_stack) <= 0:
                self.running = False
                break
            
            view = self.view_stack[0]
            
            try:
                if not view.step(core):
                    self.pull()
            except Exception as e:
                if len(self.try_stack) > 0:
                    core.exception_stack.push(e)
                    try_view = self.try_stack.pull()
                    view = self.pull()
                    while view is not try_view:
                        view = self.pull()
                else:
                    raise e
                