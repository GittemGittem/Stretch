from .core import precedence, operators, commands
from .core_types import StretchTerminate, Stack, Promise

class SetVar:
    __slots__ = ("token",)
    def __init__(self, token:'RawToken'):
        if isinstance(token, str):
            token = RawToken(token)
        self.token = token

class RawToken:
    __slots__ = ("literal",)
    __raw__ = {}
    def __init_subclass__(cls):
        cls.__raw__ = dict()
    
    def __deepcopy__(self, memo):
        return self
    
    def __new__(cls, literal:str):
        if issubclass(type(literal), RawToken):
            literal = literal.literal

        if literal in cls.__raw__:
            instance = cls.__raw__[literal]
        else:
            instance = super().__new__(cls)
            instance.literal = literal
            cls.__raw__[literal] = instance
        return instance
    
    def __hash__(self):
        return hash((self.__class__, self.literal))
    
    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return self.literal == other.literal
        return False
    def __repr__(self):
        return f"({type(self).__name__}:'{self.literal}')"
    
    def dot(self):
        return self.literal
    def file(self, ext=None):
        if ext is not None: ext = "." + ext
        return self.literal + ext or ""
    

class Op(RawToken): pass

class Expression:
    def __init__(self, expr):
        self.expr = expr
    
    def load_vars(self, view):
        index = 0
        copy = self.expr[:]
        index = 0
        while index < len(copy):
            val = copy[index]
            if not isinstance(val, Op):
                if isinstance(val, RawToken):
                    copy[index] = view.get_var(val)
                if isinstance(val, Dotpath):
                    copy[index] = view.get_var(val)
                elif isinstance(val, Expression):
                    copy[index] = val.load_vars(view)
            
            index += 1
        return Expression(copy)
    def resolve(self, precedence, operations, solve):
        solution = solve.expr[:]
        for group in precedence:
            index = 0
            while index < len(solution) - 1:
                
                term = solution[index]
                if isinstance(term, Op):
                    op = term.literal
                    if op in group:
                        if op in operators:
                            index -= 1
                            l = solution.pop(index)
                            _ = solution.pop(index)
                            r = solution.pop(index)
                            if isinstance(l, Expression):
                                l = l.resolve(precedence, operations, l)
                            if isinstance(r, Expression):
                                r = r.resolve(precedence, operations, r)
                            value = operators[op](l, r)
                            solution.insert(index, value)
                        else:
                            raise StretchTerminate(f"Undefined Operator {op}")
                index += 1
        if len(solution) > 1:
            undefined_ops = []
            for term in solution:
                if isinstance(term, Op):
                    undefined_ops.append(term)
            raise StretchTerminate(f"Unresolved expression, undefined operators: {undefined_ops} in {solution}")
        return solution[0]
class Dummy:
    def __init__(self, expr):
        self.value = expr
    def load(self):
        from copy import deepcopy
        return deepcopy(self.value)
        

        
class Switch(RawToken): pass
class Command:
    __slots__ = ("command", "switches")
    def __init__(self, command:str, *switches:str):
        self.command = command
        self.switches = switches
    
    def __iter__(self):
        yield self.command
        yield self.switches
    
    def __repr__(self):
        return f"{self.command}: @{' @'.join(self.switches)}>"
                              
class Dotpath:
    __slots__ = ("chain",)
    def __init__(self, *chain):
        self.chain = chain      
    
    def file(self, ext = None):
        if ext is not None: ext = "." + ext
        return "/".join([str(seg.literal) if isinstance(seg, RawToken) else str(seg) for seg in self.chain]) + (ext or "")
    def dot(self):
        return ".".join([str(seg.literal) if isinstance(seg, RawToken) else str(seg) for seg in self.chain])
    
    
    def __repr__(self):
        return f"<{'.'.join([str(seg) for seg in self.chain])}>"

class Pointer:
    __slots__ = ("reference", "marked")
    def __init__(self, obj, mark=False):
        self.marked = mark
        self.reference = obj
    
    def __repr__(self):
        return f"[{self.reference}]"
        

class Statement:
    def __init__(self, sections):
        self.sections = sections
    def __iter__(self):
        for section in self.sections:
            yield section

class Block:
    def __init__(self, stat, init, end):
        self.stat = stat
        self.init = init
        self.end = end
        
        self.run_counter = 0
        
        self.precedence = precedence.copy()
        self.operators = operators.copy()
        self.commands = commands
        
        self.return_stack = Stack()
        self.__scope__ = {}
    
    @property
    def scope(self):
        return self
    
    def set_var(self, keys, values):
        if not isinstance(keys, tuple):
            keys = (keys,)
        if not isinstance(values, tuple):
            values = tuple([values for _ in range(len(keys))])
        for key_index in range(len(keys)):
            set_scope = self.__scope__
            token = keys[key_index]
            if isinstance(token, Dotpath):
                chain = token.chain
                index = 0
                while index < len(chain) - 1:
                    segment = chain[index].literal
                    if segment in set_scope:
                        val = set_scope[segment]
                        if isinstance(val, Block):
                            set_scope = val.__scope__
                            index += 1
                            continue
                    raise StretchTerminate(f"Encountered a gap in {chain} at {segment}")
                else:
                    token = chain[-1]
            name = token.literal
            set_scope[name] = values[key_index]
    def get_var(self, token):        
        get_scope = self.__scope__
        if isinstance(token, Dotpath):
            chain = token.chain
            index = 0
            while index < len(chain) - 1:
                segment = chain[index].literal
                if segment in get_scope:
                    val = get_scope[segment]
                    if isinstance(val, Promise):
                        val = val.load()
                    if isinstance(val, Block):
                        get_scope = val.__scope__
                        index += 1
                        continue
                raise StretchTerminate(f"Encountered a break in {chain} at index {index}: {segment}")
            else:
                token = chain[-1]
                if token.literal not in get_scope:
                    raise StretchTerminate(f"Scope {chain[-2].literal} in chain {chain} does not contain {chain[-1].literal}")
        if token.literal not in get_scope:
            raise StretchTerminate(f"No '{token.literal}' in scope.")
        
        name = token.literal
        value = get_scope[name]
        if isinstance(value, Promise):
            value = value.load()
            get_scope[name] = value
        return value       
    
    def process_section(self, interpreter, view, section):
        index = len(section) - 1
        
        while index >= 0:
            match section[index]:
                case dummy if isinstance(dummy, Dummy):
                    section.pull(index)
                    section.insert(dummy.load(), index)
                case setvar if isinstance(setvar, SetVar):
                    if setvar.token in self.operators:
                        raise StretchTerminate(f"Cannot override term {setvar.token.literal} with a variable.")
                    section.pull(index)
                    view.set_var(setvar.token, section.pull(index))
                case command if isinstance(command, Command):
                    tokens = section[index + 1:]
                    del section[index:]
                    self.commands[command](interpreter, view, tokens)
                    section.extend(tokens)
                case expr if isinstance(expr, (Expression, Dotpath, RawToken, tuple)):
                    section.pull(index)
                    section.insert(self.process_expr(interpreter, view, expr), index)
                
            index -= 1
    def process_expr(self, interpreter, view, expr):
        match expr:
            case expr if isinstance(expr, Expression):
                return expr.resolve(self.precedence.sort_groups(), self.operators, expr.load_vars(view))
            case path if isinstance(path, Dotpath):
                return view.get_var(path)
            case keys if isinstance(keys, tuple):
                result = []
                for key in keys:
                    if key in self.__scope__:
                        result.append(view.get_var(key))
                    else:
                        result.append(key)
                return tuple(result)
            case token if isinstance(token, RawToken):
                if token.literal in self.__scope__:
                    return view.get_var(token)
                else:
                    raise StretchTerminate(f"Unbound token {token}")


    