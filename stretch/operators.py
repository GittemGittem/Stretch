from .precedence import PrecedenceGraph
from garnish import garnish

precedence = PrecedenceGraph()
operators = {}


def add_group(group, low=None, high=None):
    precedence.group(group, low, high)
    
@garnish
def add_operation(operate, group:str, symbol:str):
    precedence.add_members(group, symbol)
    operators[symbol] = operate
    return operate


# OPERATORS
add_group("addition", "comparison")
add_group("multiplication", "addition")
add_group("exponentiation", "multiplication")
add_group("comparison", "equivalence")
add_group("equivalence")

@add_operation.use("addition", "+")
def __add__(l, r):
    return l + r
@add_operation.use("addition", "-")
def __sub__(l, r):
    return l - r
@add_operation.use("multiplication", "*")
def __mul__(l, r):
    return l * r
@add_operation.use("multiplication", "/")
def __div__(l, r):
    return l / r

@add_operation.use("equivalence", "==")
def __eq__(l, r):
    return l == r
@add_operation.use("equivalence", "!=")
def __ne__(l, r):
    return l != r
@add_operation.use("comparison", ">")
def __gt__(l, r):
    return l > r
@add_operation.use("comparison", "<")
def __lt__(l, r):
    return l < r
@add_operation.use("comparison", ">=")
def __ge__(l, r):
    return (l > r) or (l == r)
@add_operation.use("comparison", "<=")
def __le__(l, r):
    return (l < r) or (l == r)

