class Stack(list):
    __slots__ = ("single_layer")
    class StackError(Exception): pass
    def __init__(self, *iterable, single_layer=True):
        if single_layer:
            if any([isinstance(obj, Stack) and obj is not self for obj in iterable]):
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
            if isinstance(value, Stack) and value is not self:
                raise Stack.StackError(f"Cannot move vertically in a single layer stack")
        self.level().insert(value, 0)
    def pull(self, index=0):
        return self.level().pop(index)

    def pull_if(self, type, index=0):
        val = self.peek(index)
        if isinstance(val, type):
            self.pull(index)
            return val
        else:
            return None
    def pull_only(self, type, index=0):
        val = self.pull_if(type, index)
        if val is None:
            raise Stack.StackError(f"expected {type} at {index} on stack recieved {self.peek(index)}")
        return val
    
    def peek(self, index=0):
        if index > len(self.level()) - 1:
            return None
        return self.level()[index]

    def peek_if(self, type:type, index=0):
        val = self.peek(index)
        if not isinstance(val, type):
            return None
        return val
    def empty(self, level:int=1):
        self.level(level).clear()
    def copy(self, index = 0):
        self.push(self.peek(index))
    def surface(self, index=-1):
        self.push(self.pull(index))

    def insert(self, value, index=0):
        list.insert(self.level(), index, value)

class Channel:
    def __init__(self):
        self.channels = {}
        
    def emit(self, id, value):
        self.channels[id] = value
        
    def clear(self):
        self.channels.clear()
        
    def receive(self, id, default=None):
        value = default
        if id in self.channels:
            value = self.channels[id]
        return value
    
    def take(self, id, default=None):
        value = default
        if id in self.channels:
            value = self.channels[id]
            del self.channels[id]
        return value
class StretchTerminate(Exception):
    def __init__(self, *objects):
        message = ""
        for object in objects:
            message += str(object)
        if message == "":
            message = "Exception with no defined message"
        super().__init__(("\x1b[31m" + message + "\x1b[0m").encode().decode())
        
class Promise:
    def __init__(self, block):
        self.return_stack = block.return_stack
    
    def load(self):
        if len(self.return_stack) > 0:
            return self.return_stack.pull()
        else:
            return None