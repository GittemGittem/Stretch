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
        self.block = block
    
    def load(self):
        if len(self.block.return_stack) > 0:
            return self.block.return_stack.pull()
        else:
            return self.block
        
class CommandInterface:
    def __init__(self):
        self.commands = {}
    def __setitem__(self, keys, command):
        index = 0
        current_dict = self.commands
        while index < len(keys):
            key = keys[index]
            if not dict.__contains__(current_dict, key):
                dict.__setitem__(current_dict, key, {'.':None})
            current_dict = dict.__getitem__(current_dict, key)
            index += 1
        dict.__setitem__(current_dict, '.', command)
    
    def __deepcopy__(self, memo):
        return self
    
    def __getitem__(self, command):
        command, switches = command
        if command not in self.commands:
            print(self)
            raise StretchTerminate(f"There is no registered command {command}.")
        current_dict = self.commands[command]
        prev_switch = command
        
        for switch in switches:
            if switch not in current_dict:
                raise StretchTerminate(f"There is no switch '{switch}' registered to \\{command}.")
            current_dict = current_dict[switch]
            prev_switch = switch
        return current_dict['.']
    
    def update(self, other):
        def follow(level, node):
            for key, value in node.items():
                if key == ".":
                    self[level] = value
                else:
                    follow(level + (key,), value)
        follow((), other.commands)
    def copy(self):
        return self
    
class Function:
    def __init__(self, block, params):
        self.block = block
        self.params = params
    
    @property
    def return_stack(self):
        return self.block.return_stack
    
    def call(self, interpreter, args):
        args_length, params_length =len(args), len(self.params)
        if args_length != params_length:
            raise StretchTerminate(f"Function expected {params_length} arguments, recieved {args_length}")
        for index, name in enumerate(self.params):
            self.block.set_var(name, args[index])
        from .scope_types import View, InitView
        interpreter.view_stack.push(View(self.block))
        interpreter.view_stack.push(InitView(self.block))

class Class:
    def __init__(self, block):
        self.block = block
            
    
    def new(self, interpreter, tokens):
        from .lang import Block
        from .scope_types import View, InitView
        from .core import call
        if "__new__" in self.block.__scope__:
            __new__ = self.block.__scope__["__new__"]
            __new__.block.__scope__["cls"] = self.block
            call(interpreter, 0, Stack(__new__, *tokens))
            return Promise(__new__)
        else:
            instance = Block({}, {}, 0)
            instance.__scope__["__class__"] = self.block
            return instance
            
    
    def extend(self, block, params):
        return Class(block, params or self.params, self)
        