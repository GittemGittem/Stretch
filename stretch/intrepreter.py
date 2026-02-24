from core_types import Stack, Dotpath, RawToken
import os

class Scope:
    def __init__(self, processor, *lines):
        self.processor = processor
        processor.scope_stack.push(self)
        
        self.end = 0
        self.current_line = 0
        self.parse_lines(*lines)
        
        self.__scope__ = {}
        
        self.init()
    
    def parse_lines(self, *lines):
        init_parsed = {}
        parsed = {}
        init = False
        for index in range(len(lines)):
            line = lines[index]
            if line.startswith('$'):
                line = line[1:]
                init = True
            tokens = self.parser(line)
            if init:
                init_parsed[index] = tokens
            else:
                parsed[index] = tokens
            if index > self.end:
                self.end = index
            init = False
        self.init_lines = init_parsed
        self.lines = parsed
            
    def parser(self, line):
        return self.processor.parser(line)
    
    @property
    def line(self):
        if self.current_line in self.lines:
            return self.lines[self.current_line]
        else:
            return None

    def __len__(self):
        return self.end + 1
    
    def init(self):
        current_line = 0
        while current_line < len(self):
            if current_line in self.init_lines:
                self.process(self.init_lines[current_line])
            current_line += 1
        
    def step(self):
        if self.current_line > self.end:
            return False
        
        tokens = self.line
        if tokens:
            self.process(tokens)
        self.current_line += 1
        return True
        
    def process(self, tokens):
        self.processor.process(tokens)
    
class Module(Scope):
    @staticmethod
    def load_module(dotpath):
        with open(dotpath.filepath('str'), 'r') as module_file:
            return module_file.readlines()
    def __init__(self, processor, dotpath):
        super().__init__(processor, *self.load_module(dotpath))

class Processor:
    def __init__(self):
        self.running = False
        self.scope_stack = Stack()
        self.global_stack = Stack()
            
    def mainloop(self):
        self.running = True
        while self.running:
            scope = self.scope_stack.peek_if(Scope)
            if scope is None:
                self.running = False              
                return
            
            if not scope.step():
                self.scope_stack.pull()
            
    def parser(self, line):
        tokens = []
        build_str = []
        str_end = None
        for token in line.split():
            match token:
                case token if str_end is not None:
                    if token.endswith(str_end):
                        str_end = None
                        build_str.append(token)
                        tokens.append(" ".join(build_str)[1:-1].encode("utf-8").decode("unicode_escape"))
                        build_str = []
                    else:
                        build_str.append(token)
                case token if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
                    tokens.append(token[1:-1].encode("utf-8").decode("unicode_escape"))
                case token if token.startswith('"') or token.startswith("'"):
                    str_end = token[0]
                    build_str.append(token)
                case token if token.strip('-').isdigit():
                    tokens.append(int(token))
                case token if (len(token.split('.')) == 2) and (token.strip('.').strip('-').isdigit()):
                    tokens.append(float(token))
                case token if '.' in token:
                    toks = []
                    for tok in token.split('.'):
                        toks.append(self.parser(tok))
                        print(tok)
                    print(toks)
                    tokens.append(Dotpath(*toks))
                        
                case token:
                    tokens.append(RawToken(token))
        return tokens
    
    def process(self, tokens):
        print(tokens)    
    
    
        
proc = Processor()

main = Module(proc, Dotpath("main"))

proc.mainloop()

