from .precedence import PrecedenceGraph
from .lang_types import Op, RawToken, Coreword
from garnish import garnish
default_operators = {Op("+"):lambda l, r:l + r}
default_precedence = PrecedenceGraph()
default_core = {}

@garnish
def add_operator(operation, group:str, symbol:str):
    default_precedence.add_members(group, Op(symbol))
    default_operators[Op(symbol)] = operation
    return operation
    
def add_group(name:str, low:str=None, high:str=None):
    default_precedence.group(name, low, high)

@garnish
def add_term(behavior, name):
    default_core[Coreword(name)] = behavior
    return behavior
add_group("addition")

@add_operator.use("addition", "+")
def __add__(l, r):
    return l + r

@add_term.use("print")
def _print(interpreter, scope, *args):
    print(*args)





