from lark import Transformer
# representative language types
from .types import *
# true usable types
from ..constructors import Stack, Block, Statement, Group, Array, Dictionary, Cluster



class StretchBuilder(Transformer):
    #start
    def start(self, block):
        return Block(block)
    #statement
    def statement(self, stat):
        init = stat[0] or False
        statement = [part for part in stat[1:] if part is not None]
        return Statement(statement, init)
    def INIT(self, init):
        return True
    def set(self, name):
        return Set(name[0])
    def get(self, get):
        return Get(get[0])
    
    
    # value
    def value(self, value):
        return value[0]
    # container
    def container(self, container):
        return container[0]
    def constructor(self, constructor):
        return Constuctor(constructor[0])
    def block(self, block):
        return Block(Array(block))
    def statement_array(self, stat):
        return Array(stat)
    def stack(self, stack):
        return Stack(stack)
    def array(self, array):
        return Array(array)
    def group(self, group):
        return Group(group)
    def cluster(self, cluster):
        return Cluster([get.var for get in cluster])
    def pair(self, pair):
        key, value = pair
        return {key: value}
    def dict(self, dictionary):
        new = Dictionary()
        for pair in dictionary:
            new.update(pair)
        return new
    
    # atom
    def atom(self, atom):
        return atom[0]
    def STR(self, string):
        return string[1:-1]
    def NUM(self, num):
        if '.' in num:
            return float(num)
        else:
            return int(num)
    
    #expr
    def expr(self, expr):
        return Expression(expr)
    def par_expr(self, par_expr):
        return ParExpression(par_expr)
    
    def OPERATOR(self, op):
        return Operator(op)
    
    def NAME(self, name):
        return str(name)
    
    def switches(self, switches):
        return switches
    def command(self, command):
        command, switches = command
        return Command(command, tuple(switches))







