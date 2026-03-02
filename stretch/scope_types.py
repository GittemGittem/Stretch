from .core_types import Stack
from copy import deepcopy
class View:
    def __init__(self, scope):
        self._scope = scope
        scope.run_counter += 1
        self._here = scope
        self.current_line = 0
        
    @property
    def scope(self):
        return self._scope
    @property
    def here(self):
        return self._here
    
    def step(self, interpreter):
        if self.current_line >= self.scope.end:
            if hasattr(self.scope, '__end__'):
                return self.scope.__end__(interpreter, self) or False
            return False
        
        
        if self.current_line in self.scope.stat:
            statement = self.scope.stat[self.current_line]
            self.here.process_section(interpreter, self, Stack(*statement))
        if self.current_line == 0:
            if hasattr(self.scope, '__start__'):
                self.current_line += 1
                return self.scope.__start__(interpreter, self) or True
        self.current_line += 1
        return True
    def get_var(self, key):
        return self.here.get_var(key)
    def set_var(self, key, value):
        return self.here.set_var(key, value)
class InitView(View):
    def step(self, interpreter):
        if self.current_line >= self.scope.end:
            return False
        
        if self.current_line in self.scope.init:
            statement = self.scope.init[self.current_line]
            self.here.process_section(interpreter, self, Stack(*statement))
        self.current_line += 1
        return True

class InitHereView(InitView):
    def __init__(self, here, scope):
        super().__init__(scope)
        self._here = here
        
    def get_var(self, key):
        return self.here.get_var(key)
    def set_var(self, key, value):
        self.here.set_var(key, value)
class HereView(View):
    def __init__(self, here, scope):
        super().__init__(scope)
        self._here = here
    def get_var(self, key):
        return self.here.get_var(key)
    def set_var(self, key, value):
        self.here.set_var(key, value)

