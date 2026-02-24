

type DotPath = None #alias

class Scope:
    def __init__(self, processor, name, parent):
        self.processor = processor
        self.name = name
        self.parent = parent
        
        self.__lines__ = []
        self.current_line = 0
        self.__scope__ = {}
    
    def store(self, name, value):
        self.__scope__[name] = value
    
    def retrieve(self, name):
        return self.__scope__[name]
    
    def swap(self, name, value):
        temp = self.__scope__[name]
        self.__scope__[name] = value
        return temp
    
    def erase(self, name):
        del self.__scope__[name]
    
    def contains(self, name):
        return name in self.__scope__
    
    def clear_line(self, line:int):
        del self.__lines__[line]
    def clear_lines(self):
        self.__lines__.clear()
    def write_line(self, line:str):
        self.__lines__.append(line.strip())
    def write_lines(self, lines:list[str]):
        for line in lines:
            self.write_line(line)
    
    def operators(self, symbol=None):
        return self.parent.operators(symbol)
    def terms(self, term=None):
        return self.parent.terms(term)

    def __iter__(self):
        while self.current_line < len(self.__lines__):
            yield self.__lines__[self.current_line]
            self.current_line += 1
    
    def go_to(self, line):
        self.current_line = line

class Module(Scope):
    @staticmethod
    def load_module(file_path):
        with open(file_path, 'r') as source:
            return source.readlines()
    
    def __new__(cls, processor, module_path:DotPath, parent=None):
        path = module_path.path_chain()
        if path in processor.modules():
            instance = processor.modules(path)
        else:
            instance = super().__new__(cls)
            processor.add_module(path, instance)
        return instance
    
    def register_operator(self, symbol:str, operation):
        if symbol not in self.__operators__:
            self.__operators__[symbol] = operation
        
    def __init__(self, processor, module_path:DotPath, parent=None):
        super().__init__(processor, module_path.file_name(), parent)
        self.path = module_path.file_name('str')
        self.write_lines(self.load_module(self.path))
        
        
        self.__operators__ = processor.__operators__
        self.__operator_precedence__ = processor.__operator_precedence__
        self.__terms__ = processor.__terms__
        self.__types__ = {}
        self.__scope__ = {}
    @property
    def operators(self):
        return self.__operators__
    @property
    def precedence(self):
        return self.__operator_precedence__.sort_groups()
    
    @property
    def terms(self):
        return self.__terms__