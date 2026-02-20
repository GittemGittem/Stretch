class extend:
    __slots__ = ("func",)
    def __init__(self, func):
        self.func = func
    
    def extend(self, interpreter):
        self.func(interpreter)

class __operator(extend):
    __slots__ = ("behavior", "symbol", "lower", "higher")
    def __init__(self, symbol, behavior, lower=None, higher=None):
        self.symbol = symbol
        self.behavior = behavior
        self.lower = lower
        self.higher = higher

    def extend(self, interpreter):
        interpreter.precedence_graph.add(self.symbol, self.lower, self.higher)
        interpreter.register_operator(self.symbol, self.behavior)
        
def operator(symbol:str, lower=None, higher=None):
    def wrap(behavior_func):
        return __operator(symbol, behavior_func, lower, higher)
    return wrap
        
class __operator_replace(__operator):
    def extend(self, interpreter):
        interpreter.precedence_graph.add(self.symbol, self.lower, self.higher)
        interpreter.set_operator(self.symbol, self.behavior)

def operator_replace(symbol:str, lower:str, higher=None):
    def wrap(behavior_func):
        return __operator_replace(symbol, behavior_func, lower, higher)
    return wrap
        
class __term(extend):
    __slots__ = ("behavior", "term")
    def __init__(self, term, behavior):
        self.term = term
        self.behavior = behavior
        
    def __call__(self, module, stack):
        self.behavior(module, stack)
        
    def extend(self, interpreter):
        interpreter.register_term(self.term, self.behavior)
        
def term(term:str):
    def wrap(behavior_func):
        return __term(term, behavior_func)
    return wrap
        
class __term_replace(__term):
    def extend(self, interpreter):
        interpreter.set_term(self.term, self.behavior)
        
def term_replace(term:str):
    def wrap(behavior_func):
        return __term_replace(term, behavior_func)
    return wrap
        