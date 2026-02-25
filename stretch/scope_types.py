
class Scope:
    __slots__ = ("init_lines", "lines", "end", "processor")
    def __new__(cls, key, processor, *lines):
        if key in processor.__scopes__:
            instance = processor.__scopes__[key]
        else:
            instance = super().__new__(cls)
            processor.__scopes__[key] = instance
        return instance
            
    
    def __init__(self, key, processor, *lines):
        self.processor = processor
        self.processor.push_scope(self)
        
        self.init_lines = {}
        self.lines = {}
        
        self.end = 0
        self.parse_lines(*lines)
        self.init()
        
        
    
    def __len__(self):
        return self.end + 1
    
    def init(self):
        current_line = 0
        while current_line < self.end:
            if current_line in self.init_lines:
                self.process(self.init_lines[current_line])
            current_line += 1
        
    
    def parse_lines(self, *lines):
        self.init_lines = {}
        self.lines = {}
        for index, line in enumerate(lines):
            if line.startswith('$'):
                self.init_lines[index] = self.parse(line[1:])
            else:
                self.lines[index] = self.parse(line)
            if index > self.end:
                self.end = index
    
    def parse(self, line):
        return self.processor.parse(line)
    
    def process(self, tokens):
        self.processor.process(self, tokens)

