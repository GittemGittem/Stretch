from garnish import garnish
from .core import __operators__, __terms__, __operator_precedence__
from .core_types import RawToken

class Extender:
    def __init__(self):
        self.__operators__ = __operators__
        self.__operator_precedence__ = __operator_precedence__.copy()
        self.__terms__ = __terms__
        self.__types__ = {}
        
        self.__direct__ = []
    
    
    def extend(self, proc, scope):
        for operator in self.__operator_precedence__.sort():
            scope.__operators__[operator] = self.__operators__[operator]
        scope.__terms__.update(self.__terms__)
        scope.__types__.update(self.__types__)
        
        for func in self.__direct__:
            func(proc, scope)
    
    
    def __enter__(self):
        return self
    def __exit__(self, *exc_args): pass
    
    def __call__(self, func):
        self.__direct__.append(func)
    
    @garnish
    def operator(self, func, symbol:str, low=None, high=None):
        if low is not None:
            low = RawToken(low)
        if high is not None:
            high = RawToken(high)
        self.__operators__[RawToken(symbol)] = func
        self.__operator_precedence__.add(RawToken(symbol), low, high)
        return func

    @garnish
    def term(self, func, term:str):
        self.__terms__[RawToken(term)] = func
        return func
    
    @garnish
    def type(self, cls):
        pass
    

