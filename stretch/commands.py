from garnish import garnish
from .structures import Stack, Group
from .view import View


commands = {}


def make_group(group_name, command_dict=commands):
    if group_name not in command_dict:
        command_dict[group_name] = {}

@garnish
def add_command(func, group, *switches, command_dict=commands):
    if group not in command_dict:
        make_group(group, command_dict=command_dict)
    command_dict[group][frozenset(switches)] = func
    return func


@add_command.use("print")
def _print(core, view, stack):
    val = stack.peek()
    if val is not None:
        print(stack.pull())
    else:
        print()
        

@add_command.use("print", "all")
def print_all(core, view, stack):
    print(*stack)
    stack.clear()
    
@add_command.use("goto")
def goto(core, view, stack):
    new_line = stack.pull_if(int)
    if new_line is not None:
        new_line = new_line - 1
    else:
        new_line = -1
    prev_line = view.current_line
    stack.push(prev_line)
    view.current_line = new_line

@add_command.use("info")
def info(core, view, stack):
    obj = stack.pull()
    stack.push(f"<stretch {type(obj).__name__} obj at '{hex(id(obj))}'>")
    
@add_command.use("info", "line")
def get_line(core, view, stack):
    stack.insert(view.current_line)
    
@add_command.use("info", "block")
def get_scope(core, view, stack):
    stack.insert(view.at)
    


@add_command.use("enter") # enter a block
def enter_block(core, view, stack):
    block = stack.pull_only(dict)
    core.push(View(block))
    stack.push(block)
    
@add_command.use("while") # enter a block until a condition if False
def while_block(core, view, stack):
    from .lang import Block
    from .view import EnterView
    condition = stack.pull_only(bool)
    block = stack.pull_only(Block)
    if condition:
        view.current_line -= 1
        view = EnterView(block, view.at)
        core.interpreter.push(view)
        
@add_command.use("for") # enter a block for each element of a container
def for_block(core, view, stack):
    from .lang import Block, Stack, Group
    from .view import ForView
    token = stack.pull_only(str)
    iterable = stack.pull_only((Stack, Group))
    block = stack.pull_only(Block)
    core.interpreter.push(ForView(iterable, token, block, view.at))
    
    

@add_command.use("enter", "here") # enter a block as if it were in the current scope
def enter_inline(core, view, stack):
    from .view import View
    block = stack.pull_only(dict)
    block["__scopes__"].push(view.at)
    core.push(View(block))
    stack.push(block)

@add_command.use("reinit") # reinit a block
def reinit_block(core, view, stack):
    from .view import View
    scope = stack.pull_only(dict)
    core.interpreter.push(View(scope))
    stack.push(scope.promise)

# FUNCTIONS

@add_command.use("def")
def make_callable(core, view, stack):
    from .structures import Group
    params = stack.pull_if(Group)
    __call__ = stack.pull_only(dict)
    func = {}
    func["__params__"] = params
    func["__call__"] = __call__
    stack.push(func)

@add_command.use("inherit")
def inherit_class(core, view, stack):
    from .view import EnterView
    inherit = stack.pull_only(dict)
    new = stack.pull_only(dict)
    new.vars["super"] = inherit
    core.interpreter.push(EnterView(new))
    stack.push(new)
        
        
@add_command.use("pass")
def do_nothing(core, view, stack):
    pass



# TERMINATING BLOCKS
@add_command.use("break")
def break_view(core, view, stack):
    core.interpreter.pull()
@add_command.use("break", "count")
def break_count(core, view, stack):
    count = stack.pull_if(int) or 1
    while count > 0:
        core.interpreter.pull()
        count -= 1
@add_command.use("break", "all")
def break_all(core, view, stack):
    from .structures import Stack
    core.interpreter.view_stack = Stack()
    
@add_command.use("end")
def terminate_program(core, view, stack):
    core.running = False  
@add_command.use("continue")
def finish_scope(core, view, stack):
    view.current_line = len(view.lines)  
@add_command.use("return")
def return_val(core, view, stack):
    view.block["__promise__"] = stack.pull()

# CONTROL FLOW
@add_command.use("if")
def if_stat(core, view, stack):
    condition = stack.pull_only(bool)
    block = stack.pull_only(dict)
    block["__scopes__"].push(view.at)
    if condition:
        view = View(block)
        core.push(view)
@add_command.use("unless")
def unless_stat(core, view, stack):
    from .lang import Block
    from .view import EnterView
    condition = stack.pull_only(bool)
    block = stack.pull_only(Block)
    if not condition:
        view = EnterView(block, view.at)
        core.interpreter.push(view)

# EXCEPTION HANDLING
@add_command.use("try")
def _try(core, view, stack):
    block = stack.pull_only(dict)
    block["__scopes__"].push(view.at)
    view = View(block)
    core.exception_stack.clear()
    core.push(view)
    core.try_stack.push(view)

@add_command.use("catch")
def catch(core, view, stack):
    exc = core.exception_stack.pull_if()
    block = stack.pull_if(dict)
    
    if exc is not None:
        view.set[["EXCEPTION"]] = exc
        view = View(block, view.at)
        core.interpreter.push(view)


@add_command.use("process")
def parse_to_stretch(core, view, stack):
    from .lang import parse
    code_string = stack.pull_only(str)
    stack.push(parse(code_string))


@add_command.use("stack", "pull")
def pull_stack(core, view, stack):
    stack.push(core.pull())
@add_command.use("stack", "push")
def pull_stack(core, view, stack):
    core.push(stack.pull())

@add_command.use("extend", "builtin")
def extension(core, view, stack):
    from . import extensions
    path = stack.pull_only(str)
    extension = getattr(extensions, path)
    extension.extend(view.block)