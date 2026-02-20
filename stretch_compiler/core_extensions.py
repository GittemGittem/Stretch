from stretch_compiler._extension import extend, operator, term
from stretch_compiler.core_types import ModuleName, Alias, RawToken

locked_operators = {"+", "-", "=", ".", "=="}
locked_terms = {
    "Line",
    "goto",
    "end",
    "next",
    "pass",
    "SCOPE",
    "True",
    "False",
    "error",
    "exit"
    }

@operator('.', '==')
def accessor(module, stack, tokens):
    name = stack.pop().token
    
    accessed_module = module.parse_token(tokens.pop())
    if name in accessed_module.__scope__:
        stack.append(accessed_module.__scope__[name])
    else:
        break_program(module, [f"{accessed_module} has no attribute called '{name}'"])

@operator('==', '-')
def is_eq(module, stack, tokens):
    stack.append(stack.pop() == module.parse_token(tokens.pop()))

@operator('!=', '==')
def not_is_eq(module, stack, tokens):
    stack.append(stack.pop() != module.parse_token(tokens.pop()))

@operator('-', '+')
def subtract(module, stack, tokens):
    stack.append(stack.pop() - module.parse_token(tokens.pop()))

@operator('+', "=")
def add(module, stack, tokens):
    stack.append(stack.pop() + module.parse_token(tokens.pop()))

@operator(':', '=')
def swap(module, stack, tokens):
    value1 = stack.pop()
    value2 = module.parse_token(tokens.pop())
    
    stack.append(value2)
    stack.append(value1)

@operator('=')
def assign(module, stack, tokens):
    name = tokens.pop()
    value = stack.pop()
    
    if '.' in name:
        module_name, name = name.split('.')
        accessed_module = module.parse_token(module_name)
        accessed_module.__scope__[name] = value
        return
    module.__scope__[name] = value
        
   


@term("goto")
def goto(module, stack):
    set_to = stack.pop()
    
    stack.append(module.current_line)
    if set_to < 0:
        set_to = 0
    module.current_line = set_to

@term("enter")
def enter(module, stack):
    if len(stack) > 1:
        stored_module = stack.pop()
        line = stack.pop()
    elif len(stack) > 0:
        stored_module = stack.pop()
        line = 0
    else:
        break_program(module, ["key term 'enter' expects at least a module as a parameter"])
        return

    stored_module.current_line = line
    stored_module.running = True
    stored_module.mainloop(stored_module.load(stored_module.path), line)
    
@term("STACK")
def return_stack(module, stack):
    stack.append(stack)

@term("Line")
def get_line(module, stack):
    if isinstance(stack[-1], Alias):
        name = stack.pop().alias
        module.__scope__[name] = module.current_line 
    stack.append(module.current_line)
    
@term("end")
def end_module(module, stack):
    if len(stack) > 0:
        print(stack.pop(0))
    module.running = False

@term("exit")
def close_program(module, stack):
    if len(stack) > 0:
        print(stack.pop(0))
    
    while module.parent is not None:
        module.running = False
        module = module.parent
    module.running = False

@term("pop")
def pop_stack(module, stack):
    stack.pop()

@term("error")
def break_program(module, stack):
    if len(stack) > 0:
        print(stack.pop(0))
    else:
        print(f"Program crashed on line {module.current_line} with no defined error message")
    
    while module.parent is not None:
        module.running = False
        module = module.parent
    module.running = False

@term("print")
def print_stack(module, stack):
    print(*reversed(stack))

@term("True")
def return_true(module, stack):
    stack.append(True)
    
@term("False")
def return_false(module, stack):
    stack.append(False)

@term("SCOPE")
def return_globals(module, stack):
    stack.append(module.__scope__)
    
@term("pass")
def ignore(module, stack):
    pass

@term("next")
def ignore_line(module, stack):
    return -1

@term("if")
def if_condition(module, stack):
    if len(stack) > 0:
        value = stack.pop()
        if value is True:
            return
        elif value is False:
            return -1
    return break_program(module, [f"if statement expected a boolean value on the stack, at line {module.current_line}"])

@term("guard")
def guard_condition(module, stack):
    if len(stack) > 0:
        value = stack.pop()
        if value is False:
            return
        elif value is True:
            return -1
    return break_program(module, [f"guard statement expected a boolean value on the stack, at line {module.current_line}"])
        


    

