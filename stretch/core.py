from .precedence import PrecedenceGraph
from .core_types import Stack, StretchTerminate, Promise
from garnish import garnish
import os, importlib
from .builtin_extensions import get_builtin

precedence = PrecedenceGraph()
operators = {}

terms = {}

def add_group(group, low=None, high=None):
    precedence.group(group, low, high)
    
@garnish
def add_operation(operate, group:str, symbol:str):
    precedence.add_members(group, symbol)
    operators[symbol] = operate
    return operate

@garnish
def add_term(behavior, name):
    terms[name] = behavior
    return behavior


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



@add_term.use("print")
def _print(interpreter, view, tokens:Stack):
    print(*tokens)
    tokens.clear()
    
# MOVEMENT

@add_term.use("goto")
def goto(interpreter, view, tokens):
    new_line = tokens.pull_if(int)
    if new_line is not None:
        new_line = new_line
    else:
        new_line = 0
    prev_line = view.current_line
    tokens.push(prev_line)
    view.current_line = new_line
    
@add_term.use("Line")
def current_line(interpreter, view, tokens):
    line = view.current_line
    tokens.push(line)

@add_term.use("process")
def process(interpreter, view, tokens:Stack):
    from .parser import parser
    code = tokens.pull_only(str)
    tokens.push(parser.parse(code))

# SCOPE

@add_term.use("init")
def init(interpreter, view, tokens:Stack):
    from .lang import Block
    scope = tokens.pull_only(Block)
    interpreter.init_scope(scope)
    tokens.push(Promise(scope))

@add_term.use("enter")
def enter(interpreter, view, tokens:Stack):
    from .lang import Block
    scope = tokens.pull_only(Block)
    interpreter.process_scope(scope)
    tokens.push(Promise(scope))

@add_term.use("init_here")
def init_inline(interpreter, view, tokens:Stack):
    from .lang import Block
    from .scope_types import InitHereView
    scope = tokens.pull_only(Block)
    veiw = InitHereView(view.scope, scope)
    interpreter.view_stack.insert(veiw)
    tokens.push(Promise(scope))

@add_term.use("enter_here")
def enter_inline(interpreter, view, tokens:Stack):
    from .lang import Block
    from .scope_types import HereView
    scope = tokens.pull_only(Block)
    veiw = HereView(view.scope, scope)
    interpreter.view_stack.insert(veiw)
    tokens.push(Promise(scope))

@add_term.use("run_here")
def run_inline(interpreter, view, tokens:Stack):
    from .lang import Block
    from .scope_types import HereView, InitHereView
    scope = tokens.pull_only(Block)

    enter_view = HereView(view.scope, scope)
    interpreter.view_stack.insert(enter_view)
    init_view = InitHereView(view.scope, scope)
    interpreter.view_stack.insert(init_view)

    tokens.push(Promise(scope))
    
@add_term.use("run")
def run_scope(interpreter, view, tokens:Stack):
    from .lang import Block
    scope = tokens.pull_only(Block)
    interpreter.process_scope(scope)
    interpreter.init_scope(scope)
    tokens.push(Promise(scope))

@add_term.use("import")
def import_module(interpreter, view, tokens:Stack):
    from .lang import Pointer
    pointer = tokens.pull_only(Pointer)
    dotpath = pointer.reference
    dot = dotpath.dot()
    if dot in interpreter.__modules__:
        scope = interpreter.__modules__[dot]
    else:
        filepath = dotpath.file("str")
        if os.path.exists(filepath):
            from .parser import parser
            with open(filepath, 'r') as module_file:
                scope = parser.parse(module_file.read())
            interpreter.__modules__[dot] = scope
        else:
            raise StretchTerminate(f"There is no module {filepath}")
    tokens.insert(scope)

@add_term.use("extend")
def import_extension(interpreter, view, tokens:Stack):
    from .lang import Pointer
    pointer = tokens.pull_only(Pointer)
    path = pointer.reference
    dot = path.dot()
    if pointer.marked:
        if dot in interpreter.__builtin__:
            extender = interpreter.__builtin__[dot]
        else:
            extender = get_builtin(path)
        extender.extend(view.scope)
    else:
        if dot in interpreter.__extensions__:
            extender = interpreter.__extensions__[dot]
        else:
            filepath = path.file("py")
            if os.path.exists(filepath):
                extender = importlib.import_module(dot).__extension__
                interpreter.__extensions__[dot] = extender
            else:
                raise StretchTerminate(f"There is no extension {filepath}")
        extender.extend(view.scope)

@add_term.use("try")
def _try(interpreter, view, tokens:Stack):
    from .lang import Block
    from .scope_types import HereView, InitHereView
    scope = tokens.pull_only(Block)
    scope_view = HereView(view.scope, scope)
    init_scope_view = InitHereView(view.scope, scope)
    interpreter.view_stack.push(scope_view)
    interpreter.view_stack.push(init_scope_view)
    interpreter.try_stack.push(scope_view)
    tokens.push(Promise(scope))

@add_term.use("catch")
def catch(interpreter, view, tokens:Stack):
    from .lang import Block, RawToken
    exc = interpreter.exception_stack.pull_if(Exception)
    if exc is not None:
        scope = tokens.pull_if(Block)
        if scope is not None:
            scope.__scope__[RawToken("EXCEPTION")] = exc
            interpreter.run_scope(scope)
            tokens.push(Promise(scope))
            return
    tokens.push(None)
    

@add_term.use("raise")
def exception(interpreter, view, tokens:Stack):
    message = tokens.pull_if(str)
    if message is None:
        message = "raised without an exception message!"
    message = f"[Line : {view.current_line}] " + message
    raise StretchTerminate(message)

# CONTROL FLOW

@add_term.use("if")
def if_stat(interpreter, view, tokens:Stack):
    from .lang import Block, RawToken
    condition = tokens.pull_only(bool)
    if condition:
        block = tokens.pull_only(Block)
        from .scope_types import HereView, InitHereView
        enter_view = HereView(view.scope, block)
        interpreter.view_stack.insert(enter_view)
        init_view = InitHereView(view.scope, block)
        interpreter.view_stack.insert(init_view)
        tokens.push(Promise(block))
        return
    tokens.push(None)
@add_term.use("unless")
def unless_stat(interpreter, view, tokens:Stack):
    from .lang import Block, RawToken
    condition = tokens.pull_only(bool)
    if condition:
        block = tokens.pull_only(Block)
        from .scope_types import HereView, InitHereView
        enter_view = HereView(view.scope, block)
        interpreter.view_stack.insert(enter_view)
        init_view = InitHereView(view.scope, block)
        interpreter.view_stack.insert(init_view)
        tokens.push(Promise(block))
        return
    tokens.push(None)

@add_term.use("exit")
def terminate_program(interpreter, view, tokens:Stack):
    interpreter.running = False
    
@add_term.use("continue")
def finish_scope(interpreter, view, tokens:Stack):
    view.current_line = view.scope.end
    
@add_term.use("return")
def return_val(interpreter, view, tokens:Stack):
    val = tokens.peek()
    if val is not None:
        view.scope.return_stack.push(val)
    interpreter.view_stack.pull()

@add_term.use("break")
def remove_scope(interpreter, view, tokens:Stack):
    count = tokens.pull_if(int) or 1
    while count > 0:
        interpreter.view_stack.pull()
        count -= 1
@add_term.use("origin")
def remove_scope(interpreter, view, tokens:Stack):
    while len(interpreter.view_stack) > 1:
        interpreter.view_stack.pull()
   
# COMMUNICATION
 
@add_term.use("push")
def push_stack(interpreter, view, tokens:Stack):
    interpreter.stack.push(tokens.pull())
@add_term.use("pull")
def pull_stack(interpreter, view, tokens:Stack):
    tokens.push(interpreter.stack.pull())
    
@add_term.use("emit")
def emit_channel(interpreter, view, tokens:Stack):
    from .lang import Pointer
    ids = tokens.pull_only(Pointer).reference
    if not isinstance(ids, tuple):
        ids = (ids,)
    values = tokens.pull()
    if not isinstance(values, tuple):
        results = []
        for _ in ids:
            results.append(values)
        values = tuple(results)
    for index in range(len(ids)):
        id = ids[index].literal
        interpreter.channels.emit(id, values[index])
    
@add_term.use("receive")
def recieve_channel(interpreter, view, tokens:Stack):
    from .lang import Pointer
    id = tokens.pull_only(Pointer).reference.literal
    tokens.push(interpreter.channels.receive(id))

@add_term.use("take")
def take_channel(interpreter, view, tokens:Stack):
    from .lang import Pointer
    ids = tokens.pull_only(Pointer).reference
    if isinstance(ids, tuple):
        result = []
        for id in ids:
            id = id.literal
            result.append(interpreter.channels.take(id))
        tokens.push(tuple(result))
        return
    
    id = ids.literal
    tokens.push(interpreter.channels.take(id))

@add_term.use("on")
def on_channel(interpreter, view, tokens:Stack):
    from .lang import RawToken, Block, Pointer
    ids = tokens.pull_only(Pointer).reference
    block = tokens.pull_only(Block)
    if not isinstance(ids, tuple):
        ids = (ids,)
    for id in ids:
        if interpreter.channels.receive(id.literal) is None:
            return
    from .scope_types import HereView, InitHereView
    enter_view = HereView(view.scope, block)
    interpreter.view_stack.insert(enter_view)
    init_view = InitHereView(view.scope, block)
    interpreter.view_stack.insert(init_view)
    tokens.push(block)

@add_term.use("open")
def open_pointer(interpreter, view, tokens:Stack):
    from .lang import Pointer, Expression
    point = tokens.pull_only(Pointer)
    val = point.reference
    tokens.insert(view.scope.process_expr(interpreter, view, val))

@add_term.use("Scope")
def open_pointer(interpreter, view, tokens:Stack):
    tokens.insert(view.scope)
