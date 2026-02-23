import sys

__types__ = {}
from garnish import garnish
@garnish
def add_type(type, determine=None):
    if determine is None:
        determine = type.__determine__
    __types__[determine] = type

class StretchTerminate(Exception): pass
class StretchSkipline(Exception): pass

class Stack(list):
    __slots__ = ("single_layer")
    class StackError(StretchTerminate): pass
    def __init__(self, *iterable, single_layer=False):
        if single_layer:
            if any([isinstance(obj, Stack) for obj in iterable]):
                raise Stack.StackError(f"Cannot move vertically in a single layer stack")
        self.single_layer = single_layer
        super().__init__(iterable)
        
    def __repr__(self):
        return f"Stack -> {list.__repr__(self)}"    
    
    def level(self, index = 1):
        if self.single_layer:
            if index != 1:
                raise Stack.StackError(f"Cannot move vertically in a single layer stack")
            return self
        current_stack = self
        stacks = [current_stack]
        while len(current_stack) > 0:
            if isinstance(list.__getitem__(current_stack, -1), Stack):
                current_stack = current_stack[-1]
                stacks.append(current_stack)
            else:
                break
        return stacks[-index]
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return list.__getitem__(self.level(), key)
        elif isinstance(key, slice):
            return Stack(*list.__getitem__(self.level(), key), single_layer=self.single_layer)
        
    
    def up(self, levels:int=1):
        if self.single_layer:
            raise Stack.StackError(f"Cannot move vertically in a single layer stack")
        for _ in range(levels):
            self.level().push(Stack())
    def down(self, levels:int = 1):
        if self.single_layer:
            raise Stack.StackError(f"Cannot move vertically in a single layer stack")
        return self.level(1 + levels).pop()
    
    def push(self, value):
        if self.single_layer:
            if isinstance(value, Stack):
                raise Stack.StackError(f"Cannot move vertically in a single layer stack")
        self.level().append(value)
    def pull(self, index=-1):
        return self.level().pop(index)

    def pull_if(self, type, index=-1):
        val = self.peek(index)
        if isinstance(val, type):
            self.pull(index)
            return val
        else:
            return None
    def pull_only(self, type, index=-1):
        val = self.pull_if(type, index)
        if val is None:
            raise Stack.StackError(f"expected {type} at {index} on stack recieved {self.peek(index)}")
        return val
    
    
    def peek(self, index=-1):
        if index > len(self.level()) - 1:
            return None
        return self.level()[index]

    def peek_if(self, index, type:type):
        val = self.peek(index)
        if not isinstance(val, type):
            return None
        return val
    def empty(self, level:int=1):
        self.level(level).clear()
    def copy(self, index = -1):
        self.push(self.peek(index))
    def surface(self, index=-1):
        self.push(self.pull(index))

                
    
    def insert(self, index, value):
        list.insert(self.level(), index, value)
    
    def take(self, *types):
        taking = []
        for type in types:
            if len(self.level(1)) < 1:
                sorted = None
                if len(taking) > 0:
                    sorted = ', '.join([obj.__class__.__name__ + ":" + f"'{str(obj)}'" for obj in taking])
                raise Stack.StackError(f"stack.take() expected ({", ".join([type.__name__ for type in types])}), recieved {{{sorted or ""}, '...'}} ")
            if not isinstance(self.peek(), type):
                sorted = None
                if len(taking) > 0:
                    sorted = ', '.join([obj.__class__.__name__ + ":" + f"'{str(obj)}'" for obj in taking])
                fin_val = self.peek(2)
                final = fin_val.__class__.__name__ + ":" + f"'{str(fin_val)}'"
                if sorted is not None:
                    final = ", " + final
                raise Stack.StackError(f"stack.take() expected ({", ".join([type.__name__ for type in types])}), recieved {{{(sorted or "") + final}}} ")
            taking.append(self.pull())
        return taking
    
    def take_if(self, *types):
        taking = []
        for type in types:
            if len(self.level()) < 1:
                return taking
            if not isinstance(self.peek(), type):
                return taking
            taking.append(self.pull())
        return taking


class RawToken:
    __slots__ = ("literal",)
    __raw__ = {}
    
    def __new__(cls, literal:str, *args):
        if literal in cls.__raw__:
            instance = cls.__raw__[literal]
        else:
            instance = super().__new__(cls)
            instance.literal = literal
            cls.__raw__[literal] = instance
        return instance
    
    def __hash__(self):
        return hash((RawToken, self.literal))
    
    def __eq__(self, other):
        if isinstance(other, RawToken):
            return self.literal == other.literal
        elif isinstance(other, str):
            return False
        return False
    
    def __repr__(self):
        return f"(Raw:'{self.literal}')"
    
class DotPath:
    __slots__ = ("chain")
    def __init__(self, *chain, scope=None):
        self.chain = []
        for segment in chain:
            if isinstance(segment, str):
                for str_seg in segment.strip().split('.'):
                    if scope is not None:
                        self.chain.append(scope.parse_raw(RawToken(str_seg)))
                    else:
                        self.chain.append(RawToken(str_seg))
            elif isinstance(segment, RawToken):
                self.chain.append(segment)
    
    def __repr__(self):
        return f"<{'.'.join([str(seg) if not isinstance(seg, RawToken) else seg.literal for seg in self.chain])}>"
    
    def extend(self, *segments, scope=None):
        for segment in segments:
            if isinstance(segment, str):
                for str_seg in segment.strip().split('.'):
                    if scope is not None:
                        self.chain.append(scope.parse_raw(RawToken(str_seg)))
                    else:
                        self.chain.append(RawToken(str_seg))
            elif isinstance(segment, RawToken):
                self.chain.append(segment)
    
    def file_name(self, ext:str=None) -> str:
        if ext is not None: ext = '.' + ext
        return "/".join([name.literal for name in self.chain]) + (ext or "")
    def end(self) -> RawToken:
        return RawToken(self.chain[-1])
        
class Alias:
    __slots__ = ("name")
    
    def __init__(self, name):
        self.name = name