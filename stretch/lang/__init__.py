from lark import Transformer
import codecs
# representative language types
from .types import *
# true usable types
from ..constructors import Stack, Block, Statement, Group

class StretchBuilder(Transformer):
    #start
    def start(self, block):
        return Block({"statements" : Stack(block)})
    #statement
    def statement(self, stat):
        init = stat[0] or False
        statement = stat[1:]
        if statement[0] is None:
            statement.pop(0)
        return Statement(statement, init)
    def INIT(self, init):
        return True
    def var(self, var):
        
        return var[0]
    def raw(self, token):
        return token[0]
    
    def set(self, set):
        
        return Set(set)
    def get(self, get):
        
        return Get(get)
    
    
    # value
    def value(self, value):
        return value[0]
    def stat(self, stat):
        return stat[0]
    def getitem(self, keys):
        keys = keys[0]
        if len(keys) > 1:
            raise Exception()
        key = keys[0]
        return GetItem(key)
    def call(self, args):
        return Call(args[0])
    # container
    def container(self, container):
        return container[0]
    def block(self, block):
        return Block({"statements" : Stack(block)})
    def stack(self, stack):
        return Stack(stack)
    def group(self, group):
        return Group(group)
    
    # atom
    def atom(self, atom):
        return atom[0]
    def STR(self, string):
        string = string[1:-1]
        return codecs.decode(string, "unicode_escape")
    def NUM(self, num):
        if '.' in num:
            return float(num)
        else:
            return int(num)
    def NONE(self, n):
        return None
    def TRUE(self, true):
        return True
    def FALSE(self, false):
        return False
    def bool(self, bool):
        return bool[0]
    
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







