from scope_types import Scope
from core_types import Stack, RawToken, Dotpath

class ScopeVeiw:
    def __init__(self, scope, start_line=0):
        self.scope = scope
        self.current_line = start_line
    
    @property
    def line(self):
        if self.current_line in self.scope.lines:
            return self.scope.lines[self.current_line]
        else:
            return None
    
    def step(self):
        if self.current_line > len(self.scope):
            return False
        
        tokens = self.line
        if tokens: self.scope.process(tokens)
        self.current_line += 1
        return True
            
    
class Processor:
    def __init__(self):
        self.__scopes__ = {}
        self.scope_stack = Stack()
        self.running = False
    
    def mainloop(self):
        self.running = True
        while self.running:
            view = self.scope_stack.peek_if(ScopeVeiw)
            if view is None:
                self.running = False
            else:
                if not view.step():
                    self.scope_stack.pull()

    def push_scope(self, scope, start_line=0):
        self.scope_stack.push(ScopeVeiw(scope, start_line))
        
        
    
    
    def parse(self, line):
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

    def process(self, scope, tokens):
        print(tokens)
        
proc = Processor()

scope = Scope("main", proc, "hello")

proc.mainloop()
