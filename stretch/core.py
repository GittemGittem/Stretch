from garnish import garnish
from .core_types import DotPath, RawToken, StretchTerminate, Alias, StretchSkipline
from .scope_types import Scope, Module
import importlib
from .precedence import PrecedenceGraph
from . import builtin_extensions

__operators__ = {}
__operator_precedence__ = PrecedenceGraph()
__terms__ = {}
@garnish
def operator(func, symbol:str, low=None, high=None):
    if low is not None:
        low = RawToken(low)
    if high is not None:
        high = RawToken(high)
    __operators__[RawToken(symbol)] = func
    __operator_precedence__.add(RawToken(symbol), low, high)
    return func
@garnish
def term(func, term:str):
    __terms__[RawToken(term)] = func
    return func


#OPERATORS
@operator.use('.')
def chain(proc, scope, l, r):
    if isinstance(l, RawToken):
        l = DotPath(l, scope=scope)
    l.extend(r, scope=scope)
    return l

@operator.use('+', "-")
def add(proc, scope, l, r):
    return l + r

@operator.use('-', "==")
def subtract(proc, scope, l, r):
    return l - r

@operator.use('==')
def is_eq(proc, scope, l, r):
    return l == r
@operator.use('!=')
def not_eq(proc, scope, l, r):
    return l != r
@operator.use('>')
def is_gt(proc, scope, l, r):
    return l > r
@operator.use('<')
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
    message = "error with no defined message"
    if len(tokens) > 0:
        message = tokens.pop(0)
    message = f"[Line:'{scope.current_line}' in '{scope.name}'] {message}"
    shutdown(proc, scope, [message])

def expects(proc, scope, owner:str, tokens, type = None):
    if not len(tokens) > 0:
        error(proc, scope, [f"{owner} expected token, recieved nothing"])
    elif type is not None and not isinstance(tokens[0], type):
        error(proc, scope, [f"{owner} expected {type.__name__} in tokens, recieved {tokens}"])


@term.use('as')
def alias(proc, scope, tokens):
    tokens.insert(0, Alias(tokens.pull_only(RawToken)))
    return tokens
    
@term.use("Stack")
def get_stack(proc, scope, tokens):
    tokens.insert(0, proc.stack())
    return tokens

@term.use("print")
def _print(proc, scope, tokens):
    print(*tokens)
    return tokens

# control scope

@term.use("import")
def import_module(proc, scope, tokens):
    dotpath = tokens.pull_only((DotPath, RawToken), 0)
    if isinstance(dotpath, RawToken):
        dotpath = DotPath(dotpath, scope)
    module = Module(proc, dotpath)
    proc.init_scope(module)
    name = tokens.pull_if(Alias, 0)
    if name is not None:
        scope.store(name.name, module)
    tokens.insert(0, module)
    return tokens
    
@term.use("extend")
def import_extension(proc, scope, tokens):
    expects(proc, scope, "extend", tokens, (DotPath, RawToken))
    dotpath = tokens.pop(0)
    if isinstance(dotpath, RawToken):
        dotpath = DotPath(dotpath, scope)
    name = dotpath.file_name()
    if name.startswith('@'):
        extension = getattr(builtin_extensions, name[1:])
    else:
        extension = __import__(name)
    if hasattr(extension, '__extensions__'):
        extension.__extensions__.extend(proc, scope)
    return tokens
    
@term.use("enter")
def enter_scope(proc, scope, tokens):
    into = tokens.pull_only(Module, 0)
    line = tokens.pull_if(int, 0)
    if line is None:
        line = 0
    else:
        line -= 1
    if into is scope:
        scope.go_to(line)
        raise StretchSkipline()

    return proc.process_scope(into, line)
          
# control-flow  

@term.use("Line")
def get_line(proc, scope, tokens):
    return scope.current_line + 1

@term.use("True")
def ret_true(proc, scope, tokens):
    tokens.insert(0, True)
    return tokens

@term.use("False")
def ret_false(proc, scope, tokens):
    tokens.insert(0, False)
    return tokens

@term.use("if")
def if_stat(proc, scope, tokens):
    expects(proc, scope, "if", tokens, bool)
    if not tokens.pop(0):
        raise StretchSkipline()
@term.use("unless")
def unless_stat(proc, scope, tokens):
    expects(proc, scope, "unless", tokens, bool)
    if tokens.pop(0):
        raise StretchSkipline()

@term.use("goto")
def goto(proc, scope, tokens):
    expects(proc, scope, "goto", tokens, int)
    
    line = scope.current_line + 1
    scope.current_line = tokens.pop() - 1
    tokens.insert(0, line)
    return tokens

@term.use("Scope")
def get_scope(proc, scope, tokens):
    tokens.insert(0, scope)
    return tokens

# type conversion
@term.use("int")
def make_int(proc, scope, tokens):
    return int(tokens.pull())


    
        
    
    


    