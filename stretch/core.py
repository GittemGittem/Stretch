from .lang.types import Set, Get, Command, Constuctor
from .constructors import Stack, Array, Group, Block

x = set()

class Core:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.stack = Stack()
        self.exception_stack = Stack()
        self.channels = None
       
    def process(self, view, part, stack):
        if len(stack) > 0:
            previous = stack[0]
            if isinstance(previous, Block.Promise):
                stack[0] = previous.load()
        match part:
            case set if isinstance(set, Set):
                set.set(view.at, stack.pull())
            case get if isinstance(get, Get):
                stack.push(get.get(view.at))
            case constructor if isinstance(constructor, Constuctor):
                stack.push(constructor.load())
            case command if isinstance(command, Command):
                result = view.at.commands(command, self, view, stack)
            case stack_part if isinstance(stack_part, Stack):
                result = Stack()
                for part in stack_part:
                    if isinstance(part, Get):
                        result.append(part.get(view.at))
                    else:
                        result.append(part)
                
                stack.push(result)
            case array_part if isinstance(array_part, Array):
                result = Array()
                for part in array_part:
                    if isinstance(part, Get):
                        result.append(part.get(view.at))
                    else:
                        result.append(part)
                
                stack.push(result)
            case group_part if isinstance(group_part, Group):
                result = []
                for part in group_part:
                    if isinstance(part, Get):
                        result.append(part.get(view.at))
                    else:
                        result.append(part)
                
                stack.push(Group(result))
            case part:
                stack.insert(part)
                
                
