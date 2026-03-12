from .precedence import PrecedenceGraph
from .commands import CommandInterface, CommandGroup
from garnish import garnish

from copy import deepcopy
class Extender:
    def __init__(self):
        self.commands = CommandInterface()
        self.precedence = PrecedenceGraph()
        self.operators = {}
        self.constructors = {}
    
    @garnish
    def CommandGroup(self, func, name):
        return CommandGroup.use(name, self.commands)(func)
    
    @garnish
    def operator(self, func, group_name:str, symbol):
        self.precedence.add_member(group_name, symbol)
        self.operators[symbol] = func
        return func
    
    def extend(self, block):
        block.commands.update(self.commands)    
        block.operators.update(self.operators)
        block.precedence.update(self.precedence)
        block.constructors.update(self.constructors)         