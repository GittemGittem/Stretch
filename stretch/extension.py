from garnish import garnish
from .core import __operators__, __terms__, __operator_precedence__
from .core_types import RawToken

class Extender:
    def __init__(self):
        self.__operators__ = __operators__.copy()
        self.__operator_precedence__ = __operator_precedence__.copy()
        self.__terms__ = __terms__.copy()
        
        self.__direct__ = []
    
    
    def extend(self, proc, scope):
        scope.__operators__.update(self.__operators__)
        scope.__operator_precedence__.update(self.__operator_precedence__)
        scope.__terms__.update(self.__terms__)
        for func in self.__direct__:
            func(proc, scope)
    
    
    def __enter__(self):
        return self
    def __exit__(self, *exc_args): pass
    
    def __call__(self, func):
        self.__direct__.append(func)
    
    def add_operator_group(self, name, low=None, high=None):
        self.__operator_precedence__.group(name, low, high)
    
    @garnish
    def operator(self, func, group:str, symbol:str):
        symbol = RawToken(symbol)
        self.__operators__[symbol] = func
        self.__operator_precedence__.add_members(group, symbol)
        return func

    @garnish
    def term(self, func, term:str):
        self.__terms__[RawToken(term)] = func
        return func


