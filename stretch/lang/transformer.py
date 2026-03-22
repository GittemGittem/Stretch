from lark import Transformer, Discard
from .abstractions import *
import codecs
from ..structures import Stack, Group


class StretchTransformer(Transformer):
    def WS(*args):
        return Discard

    def NAME(self, name):
        return name[:]
    
    def start(self, all):
        return all[0]

    def code(self, code):
        block = {}
        
        if len(code) > 0:
            
            block["statements"] = Stack(code)
            
        return block

    def pair(self, key_value):
        return Pair(key_value)
    
    def block(self, code):
        return code[0]
    
    def statement(self, parts):
        return Statement(parts)
    def init_statement(self, stat):
        stat = Statement(stat[0])
        stat.init = True
        return stat
    
    def command(self, cmd):
        command = cmd[0]
        switches = ()
        if len(cmd) > 1:
            switches = cmd[1]
        return Command(command, *switches)
    def switches(self, switches):
        return switches
    
    def var(self, path):
        return path
    def set(self, path):
        return Set(*path[0])
    def get(self, path):
        return Get(*path[0])

    # container
    def container(self, container):
        return container[0]
    def stack(self, stack):
        return Stack(stack)
    def group(self, group):
        return Group(group)
    
    
    def getitem(self, getitem):
        item, get = getitem
        return Getitem(item, get)
    def call(self, call):
        obj, args = call
        return Call(obj, args)
    
    # expr
    def expression(self, expr):
        return expr
    def par_expr(self, expr):
        return Expression(expr)
    def expr(self, expr):
        return Expression(expr)
    
    def OPERATOR(self, op):
        return op[:]
    
    # value
    def value(self, val):
        return val[0]
    
    # atom
    def atom(self, atom):
        return atom[0]
    def NUM(self, num):
        if "." in num:
            return float(num)
        else:
            return int(num)
    def str(self, string):
        string = string[0]
        if isinstance(string, list):
            string = ".".join(string)
        return string
    def STR(self, string):
        return codecs.decode(string[1:-1], "unicode-escape")
    def TRUE(self, true):
        return True
    def FALSE(self, false):
        return False


transformer = StretchTransformer()