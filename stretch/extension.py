from .precedence import PrecedenceGraph
from .core_types import CommandInterface
from garnish import garnish

class Extender:
    
    def __init__(self):
        self.operators = {}
        self.commands = CommandInterface()
        self.precedence = PrecedenceGraph()
        
        self.direct = []
    
    def extend(self, scope):
        scope.operators.update(self.operators)
        scope.commands.update(self.commands)
        scope.precedence.update(self.precedence)
        
        for func in self.direct:
            func(scope)
    def __enter__(self):
        return self
    def __exit__(*args):
        pass
    
    
    def __call__(self, func):
        self.direct.append(func)
    
    def add_group(self, name:str, low:str=None, high:str=None):
        self.precedence.group(name, low, high)
    
    @garnish
    def operator(self, func, group:str, symbol:str):
        self.precedence.add_members(group, symbol)
        self.operators[symbol] = func
    
    @garnish
    def command(self, func, *switches):
        self.commands[*switches] = func
    
    
        