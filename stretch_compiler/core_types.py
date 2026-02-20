class RawToken:
    __slots__ = ("token",)
    def __init__(self, token):
        self.token = token
    
    def __repr__(self):
        return f"raw:{self.token}"

class Alias:
    __slots__ = {"alias"}
    def __init__(self, module, stack):
        self.alias = stack.pop().token
        stack.append(self)
    
    def __repr__(self):
        return f"Alias: {self.alias}"

class ModuleName:
    __slots__ = {"path", "name"}
    def __init__(self, path):
        self.path = path
        self.name = ".".join(self.path.split(".")[-1:])
    
    def __repr__(self):
        return f"<ModuleName: {self.name}>"