from stretch.extension import Extender
import math

__extensions__ = Extender()
with __extensions__ as extend:
    
    extend.add_operator_group("exponentiation", "multiplication")
    extend.add_operator_group("multiplication", "addition")
    extend.add_operator_group("addition", "equivalence")
    
    @extend.operator.use("exponentiation", "^")
    def __pow__(proc, scope, l, r):
        return math.pow(l, r)
    
    @extend.operator.use("multiplication", "*")
    def __mul__(proc, scope, l, r):
        return l * r
    
    @extend.operator.use("multiplication", "/")
    def __div__(proc, scope, l, r):
        return l / r
    
    @extend.operator.use("addition", "+")
    def __add__(proc, scope, l, r):
        return l + r

    @extend.operator.use("addition", "-")
    def __subtract__(proc, scope, l, r=None):
        if r is None:
            return -l
        return l - r
    
    @extend.term.use("int")
    def make_int(proc, scope, tokens):
        tokens.insert(int(tokens.pull()))
    
    @extend.term.use("float")
    def make_float(proc, scope, tokens):
        tokens.insert(float(tokens.pull()))
    