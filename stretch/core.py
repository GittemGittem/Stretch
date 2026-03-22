from .structures import Stack


class Core:
    __slots__ = ("stack", "view_stack", "recursion_limit", "exception_stack", "try_stack", "interface")
    def __init__(self, interface=None):
        self.stack = Stack()
        self.view_stack = Stack()
        self.interface = interface
        self.recursion_limit = 2000
        self.exception_stack = Stack()
        self.try_stack = Stack()
    
    def step(self, driver):
        view = self.view
        
        if view:
            
            next = view.next(self)
            if next:
                if next is True:
                    return next
                part, stack = next
                
                driver.process(self, view, part, stack)

                return True
            self.pull()
            return True
        return False
        
    
    def pull(self):
        return self.view_stack.pull()
    def push(self, view):
        self.view_stack.push(view)

    
    @property
    def view(self):
        if len(self.view_stack) > self.recursion_limit:
            raise RecursionError("2000 views were pushed to the view stack")
        return self.view_stack.peek()