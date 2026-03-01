from .core_types import Stack
class View:
    def __init__(self, scope):
        self._scope = scope
        self.current_line = 0
    
    @property
    def scope(self):
        return self._scope
    
    def step(self, interpreter):
        if self.current_line >= self.scope.end:
            return False
        
        if self.current_line in self.scope.stat:
            statement = self.scope.stat[self.current_line]
            self.scope.process_section(interpreter, self, Stack(*statement))
        self.current_line += 1
        return True
    def get_var(self, key):
        return self.scope.get_var(key)
    def set_var(self, key, value):
        return self.scope.set_var(key, value)

class InitView(View):
    def step(self, interpreter):
        if self.current_line >= self.scope.end:
            return False
        
        if self.current_line in self.scope.init:
            statement = self.scope.init[self.current_line]
            self.scope.process_section(interpreter, self, Stack(*statement))
        self.current_line += 1
        return True

class InitHereView(InitView):
    def __init__(self, here, scope):
        super().__init__(scope)
        self.here = here
        
    @property
    def scope(self):
        return self.here
    def step(self, interpreter):
        if self.current_line >= self._scope.end:
            return False
        
        if self.current_line in self._scope.init:
            statement = self._scope.init[self.current_line]
            self.here.process_section(interpreter, self, Stack(*statement))
        self.current_line += 1
        return True
    def get_var(self, key):
        return self.here.get_var(key)
    def set_var(self, key, value):
        self.here.set_var(key, value)
 
class HereView(View):
    def __init__(self, here, scope):
        super().__init__(scope)
        self.here = here
    
    @property
    def scope(self):
        return self.here    
    
    def step(self, interpreter):
        
        if self.current_line >= self._scope.end:
            return False
        
        if self.current_line in self._scope.stat:
            statement = self._scope.stat[self.current_line]
            self.here.process_section(interpreter, self, Stack(*statement))
        self.current_line += 1
        return True
    def get_var(self, key):
        return self.here.get_var(key)
    def set_var(self, key, value):
        self.here.set_var(key, value)

    