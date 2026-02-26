from .parser import parser
from .lang_types import Dotpath

class BlockView:
    def __init__(self, scope, startline=0):
        self.scope :Scope = scope
        self.current_line = startline
    
    def init(self, interpreter, Processor, *args):
        if hasattr(self.scope, '__start__'):
            self.scope.__start__(interpreter, self.scope, *args)
        else:
            if len(args) > 0:
                raise TypeError(f"Scope {self.__scope__} does not take arguments")
        if not self.scope.initialized:
            self.scope.process = Processor()
            for statement in self.scope.init_statements:
                self.scope.process(interpreter, self, statement)
            self.scope.initialized = True
            
    def set_var(self, name, value):
        self.scope.set_var(name, value)
    def get_var(self, name):
        return self.scope.get_var(name)
    def __contains__(self, name):
        return self.scope.__contains__(name)
    
    def step(self, interpreter):
        if self.current_line > len(self.scope.reg_statements) - 1:
            return False
        
        self.scope.process(interpreter, self, self.scope.reg_statements[self.current_line])
        self.current_line += 1
        return True
        

class Scope:
    def __init__(self, init=None, stats=None):
        self.init_statements = init or list()
        self.reg_statements = stats or list()
        self.initialized = False
        
        self.__scope__ = {}
    
    def set_var(self, name, value):
        self.__scope__[name] = value
    def get_var(self, name):
        return self.__scope__[name]
    def __contains__(self, name):
        return name in self.__scope__
    
    def process(self, interpreter, statement):
        interpreter.process(self, statement)

class Function(Scope):
    def __init__(self, params, init=None, stats=None):
        super().__init__(init, stats)
        self.params = params
    
    def __start__(self, interpreter, scope, *args):
        index = 0
        self.initialized = False
        self.__scope__ = {}
        while index < len(self.params) - 1:
            scope.set_var(self.params[index], args[index])
            index += 1
        else:
            if index + 1 != len(self.params):
                raise SyntaxError(f"Function {scope} expected a different number of arguments")
            
        
class Module(Scope):
    def load(self, dotpath):
        with open(dotpath.filepath('str'), 'r') as module_file:
            code = parser.parse(module_file.read())
            for stat in code:
                match stat[1]:
                    case "regular":
                        self.reg_statements.append(stat[0])
                    case "init":
                        self.init_statements.append(stat[0])
                
    def __init__(self, dotpath):
        super().__init__()
        self.path = dotpath
        self.load(dotpath)