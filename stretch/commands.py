from garnish import garnish


class CommandInterface:
    __slots__ = ("commands",)
    def __init__(self):
        self.commands = {}
    
    def __setitem__(self, name, command):
        self.commands[name] = command
    def __getitem__(self, name):
        return self.commands[name]
    
    def __call__(self, command, *arguments):
        return self.commands[command.command](command.switches, *arguments)


@garnish
class CommandGroup:
    __slots__ = ("commands",)
    def __init__(self, base_command, name):
        commands[name] = self
        self.commands = {frozenset(): base_command}
    
    @garnish
    def switch(self, command, *switches):
        self.commands[frozenset(switches)] = command
    def __call__(self, switches, *arguments):
        return self.commands[frozenset(switches)](*arguments)


commands = CommandInterface()




# PRINT
@CommandGroup.use("print")
def _print(core, view, stack):
    print(stack.pull())

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

info = CommandGroup.use("info")(None)
@info.switch.use("line")
def get_line(core, view, stack):
    stack.insert(view.current_line)
@info.switch.use("scope")
def get_scope(core, view, stack):
    stack.insert(view.at)
    
    
@CommandGroup.use("run") # initialize and enter a block
def run_block(core, view, stack):
    from .constructors import Block
    from .view import BlockView
    scope = stack.pull_only(Block)
    core.interpreter.push(BlockView(scope))
    stack.push(scope.promise)

@run_block.switch.use("enter") # enter a block
def enter_block(core, view, stack):
    from .lang import Block
    from .view import BlockView
    scope = stack.pull_only(Block)
    view = BlockView(scope)
    view.init = False
    core.interpreter.push(view)
    stack.push(scope.promise)

@run_block.switch.use("here") # run a block as if it were in the current scope
def run_inline(core, view, stack):
    from .lang import Block
    from .view import BlockView
    scope = stack.pull_only(Block)
    view = BlockView(scope, view.at)
    core.interpreter.push(view)
    stack.push(scope.promise)

@run_block.switch.use("enter", "here") # enter a block as if it were in the current scope
def run_inline(core, view, stack):
    from .lang import Block
    from .view import BlockView
    scope = stack.pull_only(Block)
    view = BlockView(scope, view.at)
    view.init = False
    core.interpreter.push(view)
    stack.push(scope.promise)
    
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
    from .view import BlockView
    from .types import Elif
    condition = stack.pull_only(bool)
    block = stack.pull_only(Block)
    elifs = []
    while stack.peek_if(Elif) is not None:
        elifs.append(stack.pull())
    if condition:
        view = BlockView(block, view.at)
        core.interpreter.push(view)
    else:
        for _elif in elifs:
            if _elif.condition:
                view = BlockView(_elif.block, view.at)
                core.interpreter.push(view)
                return
@CommandGroup.use("elif")
def elif_stat(core, view, stack):
    from .types import Elif
    from .lang import Block
    condition = stack.pull_only(bool)
    block = stack.pull_only(Block)
    stack.push(Elif(block, condition))
@CommandGroup.use("elun")
def elif_stat(core, view, stack):
    from .types import Elif
    from .lang import Block
    condition = not stack.pull_only(bool)
    block = stack.pull_only(Block)
    stack.push(Elif(block, condition))
@CommandGroup.use("unless")
def unless_stat(core, view, stack):
    from .lang import Block
    from .view import BlockView
    from .types import Elif
    condition = stack.pull_only(bool)
    block = stack.pull_only(Block)
    elifs = []
    while stack.peek_if(Elif) is not None:
        elifs.append(stack.pull())
    if not condition:
        view = BlockView(block, view.at)
        core.interpreter.push(view)
    else:
        for _elif in elifs:
            if _elif.condition:
                view = BlockView(_elif.block, view.at)
                core.interpreter.push(view)
                return

@CommandGroup.use("True")
def return_true(core, view, stack):
    stack.insert(True)
@CommandGroup.use("False")
def return_false(core, view, stack):
    stack.insert(False)
@CommandGroup.use("None")
def return_none(core, view, stack):
    stack.insert(None)

# EXCEPTION HANDLING
@CommandGroup.use("try")
def _try(core, view, stack):
    from .constructors import Block
    from .view import BlockView
    block = stack.pull_only(Block)
    view = BlockView(block, view.at)
    core.exception_stack.clear()
    core.interpreter.push(view)
    core.interpreter.try_stack.push(view)

@CommandGroup.use("catch")
def catch(core, view, stack):
    from .lang import Block
    from .view import BlockView
    exc = core.exception_stack.pull_if(Exception)
    block = stack.pull_if(Block)
    view.at.__scope__["EXCEPTION"] = exc
    if exc is not None:
        view = BlockView(block, view.at)
        core.interpreter.push(view)


"""
    
# MOVEMENT


@add_command.use("process")
def process(interpreter, view, tokens:Stack):
    from .parser import parser
    code = tokens.pull_only(str)
    tokens.push(parser.parse(code))


# RUNNING BLOCKS

# FUNCTIONS
@add_command.use("def")
def define(interpreter, view, tokens):
    from .lang import Block
    params = tokens.pull_if(list) or []
    block = tokens.pull_only(Block)
    tokens.push(Function(block, params))
    # TCLSH REMEMBER
@add_command.use("def", "method")
def define(interpreter, view, tokens):
    from .lang import Block
    self = tokens.pull_only(Block)
    params = tokens.pull_if(list) or []
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
    
    
    








@add_command.use("raise")
def make_exception(interpreter, view, tokens:Stack):
    message = tokens.pull_if(str)
    if message is None:
        message = "raised without an exception message!"
    message = f"[Line : {view.current_line}] " + message
    raise StretchTerminate(message)



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
@add_command.use("extend")
def import_extension(interpreter, view, tokens:Stack):
    from .lang import MarkedArray
    pointer = tokens.pull_only(list)
    path = pointer[0]
    dot = path.dot()
    if isinstance(pointer, MarkedArray):
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