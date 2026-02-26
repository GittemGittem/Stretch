class Dotpath:
    __slots__ = ("chain",)
    def __init__(self, *segments):
        self.chain = list([seg.literal if isinstance(seg, RawToken) else seg for seg in segments])
    
    def __repr__(self):
        return f"<{'.'.join([str(seg) for seg in self.chain])}>"
    
    def filepath(self, ext=None):
        if ext is not None: ext = '.' + ext
        return f"{'/'.join([str(seg) for seg in self.chain])}" + (ext or "")

class RawToken:
    __slots__ = ("literal",)
    __raw__ = {}
    def __init_subclass__(cls):
        cls.__raw__ = dict()
    
    def __new__(cls, literal:str):
        if isinstance(literal, list):
            literal = literal[0]
        if issubclass(type(literal), RawToken):
            literal = literal.literal
        if not isinstance(literal, str):
            raise SyntaxError(f"Cannot create {cls.__name__} from {literal}")
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
    
class Op(RawToken): pass

class Coreword(RawToken): pass

class __expr_meta(type):
    def __call__(cls, expr):
        if len(expr) < 2:
            return expr[0]
        else:
            return super().__call__(expr)
class Expression(metaclass=__expr_meta):
    def __init__(self, expr:list):
        self.expr = expr
    def __len__(self):
        return len(self.expr)
    def __repr__(self):
        return f"({' '.join([str(exp) for exp in self.expr])})"
    
    def resolve(self, precedence):
        print(precedence)
        index = 0
        while index < len(self.expr):
            item = self.expr[index]
            if isinstance(item, Expression):
                yield from item.resolve(precedence)
            elif isinstance(item, Op):
                index -= 1
                yield self.expr.pop(index), self.expr.pop(index), self.expr.pop(index)
                continue
            
            index += 1

class Assign:
    def __init__(self, assign):
        self.to = assign

class Block:
    def __init__(self, statements):
        self.init = []
        self.reg = []
        self.params = tuple()
        for stat in statements:
            match stat[1]:
                case "regular":
                    self.reg.append(stat[0])
                case "init":
                    self.init.append(stat[0])
class CallBlock:
    def __init__(self, name, args:tuple):
        self.name = name
        self.args = args
class CallCoreWord:
    def __init__(self, name, args:tuple):
        self.name = name
        self.args = args