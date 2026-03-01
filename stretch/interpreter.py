from .scope_types import View, InitView
from .core_types import Stack, Channel


class Interpreter:
    def __init__(self, parent=None):
        self.parent = parent
        self.__modules__ = {}
        self.__extensions__ = {}
        self.__builtin__ = {}
    
        self.view_stack = Stack()
        self.try_stack = Stack()
        self.exception_stack = Stack()
        self.running = False
        
        self.stack = Stack()
        self.channels = Channel()
    
    def init_scope(self, scope):
        view = InitView(scope)
        self.view_stack.insert(view)
    
    def process_scope(self, scope):
        view = View(scope)
        self.view_stack.insert(view)
    
    def run_scope(self, scope):
        initview = InitView(scope)
        view = View(scope)
        self.view_stack.insert(view)
        self.view_stack.insert(initview)
    
    def inline_scope(self, scope):
        inline_interpreter = Interpreter(self)
        inline_interpreter.run_scope(scope)
        inline_interpreter.mainloop()
    
    
    
    def mainloop(self):
        self.running = True

        while self.running:
            if len(self.view_stack) > 2000:
                raise RecursionError()
            view = self.view_stack.peek()
            if view is None:
                self.running = False
                return
        
            try:
                if not view.step(self):
                    self.view_stack.pull()
            except Exception as e:
                if len(self.try_stack) > 0:
                    try_view = self.try_stack.pull()
                    view = self.view_stack.pull()
                    while view is not try_view:
                        view = self.view_stack.pull()
                    self.exception_stack.push(e)
                else:
                    raise e
                
        