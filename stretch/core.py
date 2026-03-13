from .lang.types import Set, Get, Command, Expression, Operator, GetItem, Call
from .constructors import Stack, Group, Block, Promise
from .view import InitView
from copy import deepcopy

class Core:
    def push(self, val):
        self.stack.push(val)
    def pull(self):
        return self.stack.pull()
    
    
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.stack = Stack()
        self.exception_stack = Stack()
        self.channels = None
    
    def solve(self, expr, scope):
        expr = expr[:]
        operators = scope.operators
        precedence = scope.precedence
        for group in precedence:
            index = 0
            while index < len(expr):
                term = expr[index]
                if isinstance(term, Operator):
                    if term.var in group:
                        index -= 1
                        l = expr.pop(index)
                        op = expr.pop(index).var
                        r = expr.pop(index)
                        if isinstance(l, Get):
                            l = l.get(scope)
                        if isinstance(r, Get):
                            r = r.get(scope)
                        if isinstance(l, Expression):
                            l = self.solve(l, scope)
                        if isinstance(r, Expression):
                            r = self.solve(r, scope)
                        expr.insert(index, operators[op](l, r))
                index += 1
        return expr[0]
    
    def process(self, view, part, stack):
        if len(stack) > 0:
            previous = stack[0]
            if isinstance(previous, Promise):
                promise = stack.pull()
                val = promise.peek() or promise.owner
                stack.insert(val, 0)
        match part:
            case string if isinstance(string, str):
                stack.push(string.encode().decode())
            case set if isinstance(set, Set):
                set.set(view.at, stack.pull())
            case get if isinstance(get, Get):
                stack.push(get.get(view.at))
            case command if isinstance(command, Command):
                result = view.at.commands(command, self, view, stack)
            case block if isinstance(block, Block):
                block = deepcopy(block)
                self.interpreter.push(InitView(block))
                stack.push(block)
            case expr if isinstance(expr, Expression):
                expr = self.solve(expr, view.at)
                stack.push(expr)
            case stack_part if isinstance(stack_part, Stack):
                stack_part = deepcopy(stack_part)
                result = Stack()
                for part in stack_part:
                    if isinstance(part, Get):
                        result.append(part.get(view.at))
                    else:
                        result.append(part)
                stack.push(result)
            case group_part if isinstance(group_part, Group):
                group_part = deepcopy(group_part)
                result = []
                for part in group_part:
                    if isinstance(part, Get):
                        result.append(part.get(view.at))
                    else:
                        result.append(part)
                
                stack.push(Group(result))
            case part:
                stack.insert(part)
        if len(stack) > 1:
            if isinstance(stack.peek(1), Call):
                obj = stack.pull()
                call = stack.pull()
                call(self, stack, obj)
            elif isinstance(stack.peek(1), GetItem):
                obj = stack.pull()
                getitem = stack.pull()
                getitem(self, stack, obj)
                
