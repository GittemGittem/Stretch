from garnish import garnish
from copy import deepcopy


class CommandInterface:
    __slots__ = ("commands",)
    def __init__(self):
        self.commands = {}
    
    
    def update(self, other):
        for command_name in other.commands:
            if command_name in self.commands:
                command_group = other.commands[command_name]
                self.commands[command_name].update(command_group)
            else:
                self.commands[command_name] = other.commands[command_name]

    
    def __setitem__(self, name, command):
        self.commands[name] = command
    def __getitem__(self, name):
        return self.commands[name]
    
    def __call__(self, command, *arguments):
        return self.commands[command.command](command.switches, *arguments)

commands = CommandInterface()

class __cmd_group_meta(type):
    def __call__(cls, func, name, *args):
        instance = super().__call__(func, name, *args)
        if func is None:
            return instance
        func.switch = instance.switch
        return func
@garnish
class CommandGroup(metaclass = __cmd_group_meta):
    __slots__ = ("commands",)
    def __init__(self, base_command, name, interface=commands):
        interface[name] = self
        self.commands = {frozenset(): base_command}
    
    
    def update(self, other):
        for switches in other.commands:
            if other.commands[switches] is not None:
                self.commands[switches] = other.commands[switches]
    
    @garnish
    def switch(self, command, *switches):
        self.commands[frozenset(switches)] = command
        return self
    def __call__(self, switches, *arguments):
        return self.commands[frozenset(switches)](*arguments)





# PRINT
@CommandGroup.use("print")
def _print(core, view, stack):
    if stack.peek() is not None:
       print(stack.peek())
    else:
        print()

@_print.switch.use("all")
def print_all(core, view, stack):
    print(*stack)
    stack.clear()
    
@CommandGroup.use("goto")
def goto(interpreter, view, stack):
    new_line = stack.pull_if(int)
    if new_line is not None:
        new_line = new_line - 1
    else:
        new_line = -1
    prev_line = view.current_line
    stack.push(prev_line)
    view.current_line = new_line

@CommandGroup.use("info")
def info(core, view, stack):
    obj = stack.pull()
    stack.push(f"<stretch {type(obj).__name__} obj at '{hex(id(obj))}'>")
    
@info.switch.use("line")
def get_line(core, view, stack):
    stack.insert(view.current_line)
@info.switch.use("block")
def get_scope(core, view, stack):
    stack.insert(view.at)
    
@CommandGroup.use("open") # run a statement
def run_stat(core, view, stack):
    from .constructors import Statement, Stack
    from .view import LineView
    stat = stack.pull_only(Statement)
    line = view.current
    stat = deepcopy(stat)
    for part in stat.parts:
        line.parts.append(part)
@run_stat.switch.use("take") # take a statement from an array
def take_stat(core, view, stack):
    stats = stack.peek()
    run_stat(core, view, stack)
    stats.pop(0)

@CommandGroup.use("enter") # enter a block
def enter_block(core, view, stack):
    from .constructors import Block
    from .view import EnterView
    scope = stack.pull_only(Block)
    core.interpreter.push(EnterView(scope))
    stack.push(scope.promise)
    
@CommandGroup.use("while") # enter a block until a condition if False
def while_block(core, view, stack):
    from .lang import Block
    from .view import EnterView
    condition = stack.pull_only(bool)
    block = stack.pull_only(Block)
    if condition:
        view.current_line -= 1
        view = EnterView(block, view.at)
        core.interpreter.push(view)
        
@CommandGroup.use("for") # enter a block for each element of a container
def while_block(core, view, stack):
    from .lang import Block, Stack, Group, Raw
    from .view import ForView
    token = stack.pull_only(Raw)
    iterable = stack.pull_only((Stack, Group))
    block = stack.pull_only(Block)
    core.interpreter.push(ForView(iterable, token.var, block, view.at))
    
    

@enter_block.switch.use("here") # enter a block as if it were in the current scope
def enter_inline(core, view, stack):
    from .lang import Block
    from .view import EnterView
    scope = stack.pull_only(Block)
    core.interpreter.push(EnterView(scope, view.at))
    stack.push(scope.promise)
    
@enter_block.switch.use("multi") # enter multiple blocks
def run_multi(core, view, stack):
    from .constructors import Block
    from .view import EnterView, MultiView
    scopes = stack.pull_only(tuple)
    enter = MultiView([EnterView(scope) for scope in scopes])
    core.interpreter.push(enter)

@CommandGroup.use("reinit") # reinit a block
def reinit_block(core, view, stack):
    from .lang import Block
    from .view import InitView
    scope = stack.pull_only(Block)
    core.interpreter.push(InitView(scope))
    stack.push(scope.promise)

# FUNCTIONS

@CommandGroup.use("def")
def make_callable(core, view, stack):
    from .constructors import Group, Block
    from .view import EnterView
    params = stack.pull_if(Group) or Group()
    callable_body = stack.pull_only(Block)
    func = Block()
    func.vars["params"] = params
    func.vars["__call__"] = callable_body
    stack.push(func)
    
@CommandGroup.use("call")
def call(core, view, stack):
    from .constructors import Group, Block
    from .view import EnterView
    from .lang import Raw
    body = stack.pull_only(Block)
    args = stack.pull_if(Group) or Group()
    body_vars = body.vars
    params = body_vars.get("params", Group())
    if "__call__" in body_vars:
        __call__ = body_vars["__call__"]
    else:
        raise Exception(f"{body} does not contain a '__call__' method")
    if len(args) != len(params):
        raise Exception(f"{body} recieved {len(args)} args, expected {len(params)}")
    func_vars = __call__.vars
    func_vars["body"] = body
    for index, name in enumerate(params):
        func_vars[name.var if isinstance(name, Raw) else name] = args[index]
    core.interpreter.push(EnterView(__call__))
    stack.push(__call__.promise)

@CommandGroup.use("inherit")
def inherit_class(core, view, stack):
    from .constructors import Block
    from .view import EnterView
    inherit = stack.pull_only(Block)
    new = stack.pull_only(Block)
    new.vars["super"] = inherit
    core.interpreter.push(EnterView(new))
    stack.push(new)
        
        
@CommandGroup.use("pass")
def do_nothing(core, view, stack):
    pass



# TERMINATING BLOCKS
@CommandGroup.use("break")
def break_view(core, view, stack):
    core.interpreter.pull()
@break_view.switch.use("break", "count")
def break_count(core, view, stack):
    count = stack.pull_if(int) or 1
    while count > 0:
        core.interpreter.pull()
        count -= 1
@break_view.switch.use("break", "all")
def break_all(core, view, stack):
    from .constructors import Stack
    core.interpreter.view_stack = Stack()
    
@CommandGroup.use("end")
def terminate_program(core, view, stack):
    core.running = False  
@CommandGroup.use("continue")
def finish_scope(core, view, stack):
    view.current_line = len(view.lines)  
@CommandGroup.use("return")
def return_val(core, view, stack):
    val = stack.peek()
    if val is not None:
        view.at.promise.return_stack.push(val)
    core.interpreter.pull()

# CONTROL FLOW
@CommandGroup.use("if")
def if_stat(core, view, stack):
    from .lang import Block
    from .view import EnterView
    condition = stack.pull_only(bool)
    block = stack.pull_only(Block)
    if condition:
        view = EnterView(block, view.at)
        core.interpreter.push(view)
@CommandGroup.use("unless")
def unless_stat(core, view, stack):
    from .lang import Block
    from .view import EnterView
    condition = stack.pull_only(bool)
    block = stack.pull_only(Block)
    if not condition:
        view = EnterView(block, view.at)
        core.interpreter.push(view)

# EXCEPTION HANDLING
@CommandGroup.use("try")
def _try(core, view, stack):
    from .constructors import Block
    from .view import EnterView
    block = stack.pull_only(Block)
    view = EnterView(block, view.at)
    core.exception_stack.clear()
    core.interpreter.push(view)
    core.interpreter.try_stack.push(view)

@CommandGroup.use("catch")
def catch(core, view, stack):
    from .lang import Block
    from .view import EnterView
    exc = core.exception_stack.pull_if(Exception)
    block = stack.pull_if(Block)
    view.at.__scope__["EXCEPTION"] = exc
    if exc is not None:
        view = EnterView(block, view.at)
        core.interpreter.push(view)

@CommandGroup.use("extend")
def import_extension(core, view, stack):
    from .constructors import Stack
    from . import extensions
    import importlib
    path = stack.pull_only(Stack)
    if path[0] == ".":
        module = getattr(extensions, Stack(path[1:]).dot())
    else:
        module = importlib.import_module(path.dot())
    if hasattr(module, "__extension__"):
        extender = module.__extension__
        extender.extend(view.block)
    else:
        raise Exception()

@CommandGroup.use("process")
def parse_to_stretch(core, view, stack):
    from.parser import parse
    code_string = stack.pull_only(str)
    stack.push(parse(code_string))


stack = CommandGroup.use("stack")(None)
@stack.switch.use("pull")
def pull_stack(core, view, stack):
    stack.push(core.pull())
@stack.switch.use("push")
def pull_stack(core, view, stack):
    core.push(stack.pull())


"""


@add_command.use("import")
def import_module(interpreter, view, tokens:Stack):
    pointer = tokens.pull_only(list)
    dotpath = pointer[0]
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
    ids = tokens.pull_only(list)
    vals = tokens.pull()
    if not isinstance(vals, tuple):
        vals = tuple([vals for _ in range(len(ids))])
    for index in range(len(ids)):
        interpreter.channels.emit(ids[index], vals[index])
                
    
@add_command.use("channel", "look")
def recieve_channel(interpreter, view, tokens:Stack):
    ids = tokens.pull_only(list)
    for id in ids:
        tokens.push(interpreter.channels.look(id))

@add_command.use("channel", "take")
def take_channel(interpreter, view, tokens:Stack):
    ids = tokens.pull_only(list)

    if any([id is None for id in ids]):
        return
    result = []
    for id in ids:
        result.append(interpreter.channels.take(ids))
    tokens.push(tuple(result))
    

@add_command.use("channel", "on")
def on_channel(interpreter, view, tokens:Stack):
    from .lang import RawToken, Block
    ids = tokens.pull_only(list)
    block = tokens.pull_only(Block)
    for id in ids:
        if interpreter.channels.look(id) is None:
            return
    from .scope_types import HereView, InitHereView
    enter_view = HereView(view.scope, block)
    interpreter.view_stack.insert(enter_view)
    init_view = InitHereView(view.scope, block)
    interpreter.view_stack.insert(init_view)
    tokens.push(block)

@add_command.use("channel", "clear")
def clear_channels(interpreter, view, tokens:Stack):
    interpreter.channels.clear()
@add_command.use("channel", "erase")
def erase_channels(interpreter, view, tokens:Stack):
    ids = tokens.pull_only(list)
    for id in ids:
        interpreter.channels.erase(id)

"""