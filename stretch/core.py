from garnish import garnish
from .core_types import DotPath, RawToken, StretchTerminate, Alias, StretchSkipline, Stack, Loop
from .scope_types import Scope, Module
import importlib
from .precedence import PrecedenceGraph
from . import builtin_extensions
from typing import Any

__operators__ = {}
__operator_precedence__ = PrecedenceGraph()
__terms__ = {}

def add_group(name, low=None, high=None):
    __operator_precedence__.group(name, low, high)

@garnish
def operator(func, group:str, symbol:str):
    __operators__[RawToken(symbol)] = func
    __operator_precedence__.add_members(group, RawToken(symbol))
    return func
@garnish
def term(func, term:str):
    __terms__[RawToken(term)] = func
    return func

add_group('assignment', high="addition")
add_group('equivalence', 'assignment')

#OPERATORS
@operator.use('assignment','.')
def chain(proc, scope, l, r):
    if isinstance(l, RawToken):
        l = DotPath(l, scope=scope)
    elif isinstance(l, Module):
        return l.retrieve(r)
    elif isinstance(l, DotPath):
        l.extend(r, scope=scope)
        return l
    else:
        return getattr(l, r.literal)

@operator.use('equivalence', '==')
def is_eq(proc, scope, l, r):
    return l == r
@operator.use('equivalence', '!=')
def not_eq(proc, scope, l, r):
    return l != r
@operator.use('equivalence', '>')
def is_gt(proc, scope, l, r):
    return l > r
@operator.use('equivalence', '<')
def is_lt(proc, scope, l, r):
    return l < r


#TERMS
# error handling

@term.use("shutdown")
def shutdown(proc, scope, tokens):
    proc.running = False
    if len(tokens) > 0:
        raise StretchTerminate(tokens.pop())
    raise StretchTerminate()

@term.use("raise")
def error(proc, scope, tokens):
    message = tokens.pull_if(str)
    if message is None:
        message = "Exception without an error message"
    raise StretchTerminate(message)

@term.use('as')
def alias(proc, scope, tokens):
    tokens.insert(Alias(tokens.pull_only(RawToken)))
    
@term.use("stack")
def get_stack(proc, scope, tokens):
    tokens.insert(list(proc.stack()))

@term.use("display")
def display(proc, scope, tokens):
    print('\x1b[97m>\x1b[0m ' + ', '.join([str(tok).encode("utf-8").decode("unicode_escape") for tok in tokens]) + ' \x1b[97m<\x1b[0m')
    tokens.clear()
@term.use("print")
def _print(proc, scope, tokens):
    item = str(tokens.pull_if(object))
    if item is None:
        item = ""
    print(item.encode("utf-8").decode("unicode_escape"))

# control scope
@term.use("import")
def import_module(proc, scope, tokens):
    dotpath = tokens.pull_only((DotPath, RawToken), 0)
    if isinstance(dotpath, RawToken):
        dotpath = DotPath(dotpath, scope)
    path = dotpath.path_chain()
    if path in proc.modules():
        module = proc.modules(path)
    else:
        module = Module(proc, dotpath)
    proc.add_module(path, module)
    name = tokens.pull_if(Alias, 0)
    if name is not None:
        scope.store(name.name, module)
    tokens.insert(module)
    
@term.use("extend")
def import_extension(proc, scope, tokens):
    dotpath = tokens.pull_only((DotPath, RawToken))
    if isinstance(dotpath, RawToken):
        dotpath = DotPath(dotpath, scope)
    name = dotpath.file_name()
    if name.startswith('@'):
        extension = getattr(builtin_extensions, name[1:])
    else:
        extension = __import__(name)
    if hasattr(extension, '__extensions__'):
        extension.__extensions__.extend(proc, scope)

@term.use("init")
def init_scope(proc, scope, tokens):
    module = tokens.pull_only(Module)
    proc.init_scope(module)
    tokens.insert(module)
    
@term.use("enter")
def enter_scope(proc, scope, tokens):
    into = tokens.pull_only(Module, 0)
    line = tokens.pull_if(int, 0)
    if line is None:
        line = 0
    else:
        line -= 1
    if into is scope:
        
        into.go_to(line)
        raise StretchSkipline()
    else:
        proc.process_scope(into, line)
          
# control-flow  

@term.use("Line")
def get_line(proc, scope, tokens):
    tokens.insert(scope.current_line + 1)

@term.use("True")
def ret_true(proc, scope, tokens):
    tokens.insert(True)

@term.use("False")
def ret_false(proc, scope, tokens):
    tokens.insert(False)
@term.use("if")
def if_stat(proc, scope, tokens):
    token = tokens.pull_only(bool)
    if not token:
        raise StretchSkipline()
@term.use("unless")
def unless_stat(proc, scope, tokens):
    token = tokens.pull_only(bool)
    if token:
        raise StretchSkipline()

@term.use("goto")
def goto(proc, scope, tokens:Stack):
    
    to = tokens.pull_if((int, Loop)) or 0
    if isinstance(to, Loop):
        to = to.start
    prev = scope.current_line + 1
    scope.current_line = to - 1
    tokens.insert(prev)

@term.use("loop")
def startloop(proc, scope, tokens:Stack):
    goal = tokens.pull_only(int)
    prev = scope.current_line
    tokens.insert(Loop(prev, goal))
@term.use("continue")
def endloop(proc, scope, tokens:Stack):
    loop : Loop = tokens.pull_only(Loop)
    loop.loop(proc, scope)
    
@term.use("break")
def breakloop(proc, scope, tokens:Stack):
    loop : Loop = tokens.pull_only(Loop)
    loop.count = loop.goal
    

@term.use("Scope")
def get_scope(proc, scope, tokens):
    tokens.insert(scope)

@term.use("end")
def end_program(proc, scope, tokens):
    proc.running = False
    raise StretchSkipline()

@term.use("catch")
def catch_error(proc, scope, tokens):
    error = proc.stack().pull_if(Exception)
    if error is None:
        raise StretchSkipline()
    else:
        tokens.push(error)


# stack
@term.use("process")
def call_line(proc, scope, tokens:Stack):
    proc.process_line(scope, tokens.pull_only(str))

@term.use("push")
def push_stack(proc, scope, tokens):
    proc.stack().push(tokens.pull())

@term.use("pull")
def pull_stack(proc, scope, tokens):
    tokens.insert(proc.stack().pull())
    
        
    
    


    