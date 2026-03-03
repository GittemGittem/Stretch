from .precedence import PrecedenceGraph
from .core_types import Stack, StretchTerminate, Promise, CommandInterface, Function, Class
from garnish import garnish
import os, importlib
from .builtin_extensions import get_builtin

precedence = PrecedenceGraph()
operators = {}

commands = CommandInterface()

def add_group(group, low=None, high=None):
    precedence.group(group, low, high)
    
@garnish
def add_operation(operate, group:str, symbol:str):
    precedence.add_members(group, symbol)
    operators[symbol] = operate
    return operate

@garnish
def add_command(behavior, *switches):
    commands[switches] = behavior
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


# PRINT

@add_command.use("print", "all")
def _print_all(interpreter, view, tokens:Stack):
    print(*tokens)
    tokens.clear()

@add_command.use("print")
def _print(interpreter, view, tokens:Stack):
    print(tokens.pull())
    
# MOVEMENT

@add_command.use("goto")
def goto(interpreter, view, tokens):
    new_line = tokens.pull_if(int)
    if new_line is not None:
        new_line = new_line
    else:
        new_line = 0
    prev_line = view.current_line
    tokens.push(prev_line)
    view.current_line = new_line
    
@add_command.use("Line")
def current_line(interpreter, view, tokens):
    line = view.current_line
    tokens.push(line)

@add_command.use("process")
def process(interpreter, view, tokens:Stack):
    from .parser import parser
    code = tokens.pull_only(str)
    tokens.push(parser.parse(code))


# RUNNING BLOCKS
@add_command.use("run") # initialize and enter a block
def run_block(interpreter, view, tokens:Stack):
    from .lang import Block
    scope = tokens.pull_only(Block)
    interpreter.process_scope(scope)
    interpreter.init_scope(scope)
    tokens.push(Promise(scope))
@add_command.use("run", "init") # initialize a block
def init_block(interpreter, view, tokens:Stack):
    from .lang import Block
    scope = tokens.pull_only(Block)
    interpreter.init_scope(scope)
    tokens.push(Promise(scope))
@add_command.use("run", "enter") # enter a block
def enter_block(interpreter, view, tokens:Stack):
    from .lang import Block
    scope = tokens.pull_only(Block)
    interpreter.process_scope(scope)
    tokens.push(Promise(scope))
@add_command.use("run", "here") # run a block as if it were in the current scope
def run_inline(interpreter, view, tokens:Stack):
    from .lang import Block
    from .scope_types import HereView, InitHereView
    scope = tokens.pull_only(Block)

    enter_view = HereView(view.scope, scope)
    interpreter.view_stack.insert(enter_view)
    init_view = InitHereView(view.scope, scope)
    interpreter.view_stack.insert(init_view)

    tokens.push(Promise(scope))
@add_command.use("run", "init", "here") # initialize a block as if it were in the current scope
def init_inline(interpreter, view, tokens:Stack):
    from .lang import Block
    from .scope_types import InitHereView
    scope = tokens.pull_only(Block)
    veiw = InitHereView(view.scope, scope)
    interpreter.view_stack.insert(veiw)
    tokens.push(Promise(scope))
@add_command.use("run", "enter", "here") # enter a block as if it were in the current scope
def enter_inline(interpreter, view, tokens:Stack):
    from .lang import Block
    from .scope_types import HereView
    scope = tokens.pull_only(Block)
    veiw = HereView(view.scope, scope)
    interpreter.view_stack.insert(veiw)
    tokens.push(Promise(scope))

# FUNCTIONS
@add_command.use("def")
def define(interpreter, view, tokens):
    from .lang import Pointer, Block
    params = tokens.pull_if(Pointer) or ()
    if isinstance(params, Pointer):
        params = params.reference
    if not isinstance(params, tuple):
        params = (params,)
    block = tokens.pull_only(Block)
    tokens.push(Function(block, params))
    
@add_command.use("def", "method")
def define(interpreter, view, tokens):
    from .lang import Pointer, Block
    self = tokens.pull_only(Block)
    params = tokens.pull_if(Pointer) or ()
    if isinstance(params, Pointer):
        params = params.reference
    if not isinstance(params, tuple):
        params = (params,)
    block = tokens.pull_only(Block)
    block.__scope__["self"] = self
    tokens.push(Function(block, params))

@add_command.use("call")
def call(interpreter, view, tokens):
    foo = tokens.pull_only(Function)
    args = []
    for param in foo.params:
        args.append(tokens.pull())
    foo.call(interpreter, args)
    tokens.push(Promise(foo.block))
    
# CLASSES
@add_command.use("class")
def make_class(interpreter, view, tokens):
    from .lang import Block
    
    class_body = tokens.pull_only(Block)
    from .scope_types import View, InitView
    interpreter.view_stack.push(View(class_body))
    interpreter.view_stack.push(InitView(class_body))
    tokens.push(Class(class_body))

@add_command.use("class", "instance")
def new_instance(interpreter, view, tokens):
    cls = tokens.pull_only(Class)
    cls.new(interpreter, tokens)
    
@add_command.use("class", "extend")
def extend_class(interpreter, view, tokens):
    from .lang import Block
    from .scope_types import View, InitView
    cls = tokens.pull_only(Class)
    class_body = tokens.pull_only(Block)
    class_body.__scope__["super"] = cls.block
    interpreter.view_stack.push(View(class_body))
    interpreter.view_stack.push(InitView(class_body))
    tokens.push(Class(class_body))
    

    
@add_command.use("bind")
def bind(interpreter, view, tokens):
    from .lang import Pointer, Block
    block = tokens.pull_only(Block)
    properties = tokens.pull_only(Pointer).reference
    if not isinstance(properties, tuple):
        properties = (properties,)
    values = tokens.pull()
    if not isinstance(values, tuple):
        values = (values,)
    if len(properties) != len(values):
        raise StretchTerminate()
    scope_dict = block.__scope__
    for index in range(len(properties)):
        scope_dict[properties[index].literal] = values[index]
    
    
# TERMINATING BLOCKS
@add_command.use("break")
def terminate_program(interpreter, view, tokens:Stack):
    interpreter.view_stack.pull()
@add_command.use("break", "count")
def remove_scope(interpreter, view, tokens:Stack):
    count = tokens.pull_if(int) or 1
    while count > 0:
        interpreter.view_stack.pull()
        count -= 1
@add_command.use("break", "all")
def remove_scope(interpreter, view, tokens:Stack):
    interpreter.view_stack = Stack()
@add_command.use("end")
def terminate_program(interpreter, view, tokens:Stack):
    interpreter.running = False  
@add_command.use("continue")
def finish_scope(interpreter, view, tokens:Stack):
    view.current_line = view.scope.end    
@add_command.use("return")
def return_val(interpreter, view, tokens:Stack):
    val = tokens.peek()
    if val is not None:
        view.scope.return_stack.push(val)
    interpreter.view_stack.pull()
@add_command.use("return", "all")
def return_val(interpreter, view, tokens:Stack):
    while len(tokens) > 0:
        view.scope.return_stack.push(tokens.pull())
    interpreter.view_stack.pull()

# CONTROL FLOW
@add_command.use("if")
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
@add_command.use("unless")
def unless_stat(interpreter, view, tokens:Stack):
    from .lang import Block, RawToken
    condition = tokens.pull_only(bool)
    if not condition:
        block = tokens.pull_only(Block)
        from .scope_types import HereView, InitHereView
        enter_view = HereView(view.scope, block)
        interpreter.view_stack.insert(enter_view)
        init_view = InitHereView(view.scope, block)
        interpreter.view_stack.insert(init_view)
        tokens.push(Promise(block))
        return
    tokens.push(None)

@add_command.use("True")
def return_true(interpreter, view, tokens:Stack):
    tokens.insert(True)
@add_command.use("False")
def return_false(interpreter, view, tokens:Stack):
    tokens.insert(False)
@add_command.use("None")
def return_none(interpreter, view, tokens:Stack):
    tokens.insert(None)

# EXCEPTION HANDLING
@add_command.use("try")
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
@add_command.use("catch")
def catch(interpreter, view, tokens:Stack):
    from .lang import Block, RawToken
    exc = interpreter.exception_stack.pull_if(Exception)
    if exc is not None:
        scope = tokens.pull_if(Block)
        if scope is not None:
            scope.__scope__["EXCEPTION"] = exc
            interpreter.run_scope(scope)
            tokens.push(Promise(scope))
            return
    tokens.push(None)
@add_command.use("raise")
def make_exception(interpreter, view, tokens:Stack):
    message = tokens.pull_if(str)
    if message is None:
        message = "raised without an exception message!"
    message = f"[Line : {view.current_line}] " + message
    raise StretchTerminate(message)



@add_command.use("import")
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
@add_command.use("extend")
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

# COMMUNICATION
# global stack
@add_command.use("stack", "push")
def push_stack(interpreter, view, tokens:Stack):
    interpreter.stack.push(tokens.pull())
@add_command.use("stack", "pull")
def pull_stack(interpreter, view, tokens:Stack):
    val = interpreter.stack.pull()
    if isinstance(val, Promise):
        val = val.load()
    tokens.push(val)
@add_command.use("stack", "look")
def pull_stack(interpreter, view, tokens:Stack):
    val = interpreter.stack.peek()
    if isinstance(val, Promise):
        val = val.load()
    tokens.push(val)
# global channels
@add_command.use("channel", "emit")
def emit_channel(interpreter, view, tokens:Stack):
    from .lang import Pointer
    ids = tokens.pull_only(Pointer).reference
    match ids:
        case ids if isinstance(ids, tuple):
            vals = tokens.pull()
            if not isinstance(vals, tuple):
                vals = tuple([vals for _ in range(len(ids))])
            for index in range(len(ids)):
                interpreter.channels.emit(ids[index], vals[index])
        case id:
            interpreter.channels.emit(id, tokens.pull())
                
    
@add_command.use("channel", "look")
def recieve_channel(interpreter, view, tokens:Stack):
    from .lang import Pointer
    match tokens.pull_only(Pointer).reference:
        case ids if isinstance(ids, tuple):
            for id in ids:
                tokens.push(interpreter.channels.receive(id))
        case id:
            tokens.push(interpreter.channels.receive(id))

@add_command.use("channel", "take")
def take_channel(interpreter, view, tokens:Stack):
    from .lang import Pointer
    ids = tokens.pull_only(Pointer).reference
    if isinstance(ids, tuple):
        result = []
        for id in ids:
            result.append(interpreter.channels.take(id))
        tokens.push(tuple(result))
        return
    tokens.push(interpreter.channels.take(ids))

@add_command.use("channel", "on")
def on_channel(interpreter, view, tokens:Stack):
    from .lang import RawToken, Block, Pointer
    ids = tokens.pull_only(Pointer).reference
    block = tokens.pull_only(Block)
    if not isinstance(ids, tuple):
        ids = (ids,)
    for id in ids:
        if interpreter.channels.receive(id) is None:
            return
    from .scope_types import HereView, InitHereView
    enter_view = HereView(view.scope, block)
    interpreter.view_stack.insert(enter_view)
    init_view = InitHereView(view.scope, block)
    interpreter.view_stack.insert(init_view)
    tokens.push(block)

@add_command.use("open")
def open_pointer(interpreter, view, tokens:Stack):
    from .lang import Pointer, Expression
    point = tokens.pull_only(Pointer)
    val = point.reference
    tokens.insert(view.scope.process_expr(interpreter, view, val))

@add_command.use("Scope")
def get_scope(interpreter, view, tokens:Stack):
    tokens.insert(view.scope)

        