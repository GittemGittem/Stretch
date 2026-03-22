from .lang.abstractions import *
from .view import View
from .structures import Group, Stack

class Driver:
    __slots__ = ("running", "interface")
    
    def __init__(self):
        self.running = False
        self.interface = None
    
    def terminate(self):
        self.running = False
    
    def mainloop(self, core, block, interface=None):
        interface.driver = self
        self.interface = interface
        init_view = View(block)
        init_view.init = True
        enter_view = View(block)
        core.push(enter_view)
        core.push(init_view)
        self.running = True
        
        while core.view is not None:
            if not self.running:
                self.interface.window.destroy()
                break
            if self.interface is not None:
                if not self.interface.update():
                    continue
            if not core.step(self):
                self.terminate()
            
        
        if "__promise__" in block:
            return_val = block["__promise__"]
            del block["__promise__"]
            return return_val
    
    def build(self, core, view, part, stack):
        start = len(stack)
        self.process(core, view, part, stack)
        return stack.pull()
    
    def process(self, core, view, part, stack):
        
        previous = stack.peek()
        if isinstance(previous, dict):
            if "__promise__" in previous:
                stack.pull()
                stack.push(previous.get("__promise__", previous))
                del previous["__promise__"]
        elif hasattr(previous, "__promise__"):
            stack.push(stack.pull().__promise__())
                
        match part:
            case group if isinstance(group, Group):
                processed = []
                for item in group:
                    processed.append(self.build(core, view, item, stack))
                
                stack.push(Group(processed))
            case part_stack if isinstance(part_stack, Stack):
                processed = []
                for item in part_stack:
                    processed.append(self.build(core, view, item, stack))
                
                stack.push(Stack(processed))
            case block if isinstance(block, dict):
                block["__nonlocal__"] = view.at
                block["__scopes__"] = Stack()
                
                init_view = View(block)
                init_view.init = True
                
                core.push(init_view)
                stack.push(block)
            case call if isinstance(call, Call):
                
                obj, args = call
                args = self.build(core, view, args, stack)
                if isinstance(obj, Get):
                    obj = view.get(obj.path)
                    
                if "__promise__" in obj:
                    obj = obj["__promise__"]
                
                params = obj.get("__params__", ())
                if len(params) != len(args):
                    raise Exception()
                __call__ = obj.get("__call__", {})
                __call__["self"] = obj
                for index, param in enumerate(params):
                    __call__[param] = args[index]
                core.push(View(__call__))
                stack.push(__call__)
            case getitem if isinstance(getitem, Getitem):
                obj, keys = getitem
                if isinstance(obj, Get):
                    obj = view.get(obj.path)
                for key in keys[:-1]:
                    obj = obj[key]
                stack.push(obj[keys[-1]])
            case set_var if isinstance(set_var, Set):
                view.set(set_var.path, stack.pull())
            case get_var if isinstance(get_var, Get):
                stack.push(view.get(get_var.path))
            case command if isinstance(command, Command):
                view.commands[command.command][command.switches](core, view, stack)

            case value:
                stack.push(value)