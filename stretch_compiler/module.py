from stretch_compiler._extension import extend
import stretch_compiler.core_extensions as core
from stretch_compiler.precedence import PrecedenceGraph
from stretch_compiler.core_types import ModuleName, Alias, RawToken

import os
from string import ascii_letters

import importlib
        
class Module:
    file_extension = '.str'
    language_name = "Stretch"
    def __init__(self, parent=None):
        self.parent = parent
        self.path = None
        self.clear()
    
    def clear(self):
        self.current_line = 0
        self.running = False
        self.__scope__ = {}
        self.__modules__ = {}
        self.__extensions__ = {}
        
        
        self.precedence_graph = PrecedenceGraph()
        self.registered_operators = {}
        self.registered_terms = {
            "import" : self.import_module,
            "extend" : self.import_extension,
            "as" : Alias
            }
        
        self.locked_operators = set()
        self.locked_terms = set()
        self.load_extension(core)
        self.locked_operators = core.locked_operators
        self.locked_terms = core.locked_terms
    
    def import_module(self, module, stack):
        if self.parent is None:
            module_name = stack.pop()
            name = module_name.name
            if module_name in self.__modules__:
                imported_module = self.__modules__[module_name]
            else:
                if len(stack) > 0:
                    if isinstance(stack[-1], Alias):
                        name = stack.pop().alias
                
                imported_module = Module(self)
                self.__modules__[module_name] = imported_module
                imported_module.mainloop(imported_module.load("/".join(module_name.path.split(".")) + ".str"))
                
                
        else:
            self.parent.import_module(module, stack)
            return
        module.__scope__[name] = imported_module
        
    def reload_module(self, imported_module, start_line=0):
        if hasattr(imported_module, 'path'):
            imported_module.mainloop(imported_module.path, start_line)
        else:
            raise Exception(f"Module {imported_module} cannot be reloaded, it has not been loaded before")
            
        

    def import_extension(self, module, stack):
        module_name = stack.pop()

        extension_module = importlib.import_module("/".join(module_name.path.split(".")))
        self.load_extension(extension_module)
        
    def load_extension(self, extension_module):
        for attr_name in vars(extension_module):
            loaded_attr = getattr(extension_module, attr_name, None)
            if isinstance(loaded_attr, extend):
                loaded_attr.extend(self)
        self.order = self.precedence_graph.sort()
        
    def set_operator(self, symbol:str, operation): # create or change a operation
        assert symbol not in self.registered_terms, f"Cannot overload key term {symbol}"
        assert symbol not in self.locked_operators, f"Cannot overload core operator {symbol}"
        self.registered_operators[symbol] = operation
        
    def register_operator(self, symbol:str, operation): # create an operation
        assert symbol not in self.registered_operators, f"{symbol} is already a registered operation"
        self.set_operator(symbol, operation)
        
    def set_term(self, term:str, behavior): # create or change a operation
        assert term not in self.registered_operators, f"Cannot overload operator {term} with a term"
        assert term not in self.locked_terms, f"Cannot overload core term {term}"
        self.registered_terms[term] = behavior
        
    def register_term(self, term:str, behavior): # create an operation
        assert term not in self.registered_operators, f"{term} is already a registered key term"
        self.set_term(term, behavior)
        
    
    def load(self, filename:str):
        assert filename.endswith(self.file_extension), f"{filename} is does not contain the appropriate extension {self.file_extension} for a {self.language_name} module."
        assert os.path.exists(filename), f"Could not find {filename}"
        
        self.path = filename
        
        with open(filename, 'r') as source:
            lines = [line for line in source.readlines() if line.strip() != ""]
        return lines
           
    
    def mainloop(self, lines:list[str], line=0):
        lines=lines[line:]
        tokens = []
        self.running = True
        while self.current_line < len(lines):
            if not self.running:
                break
            tokens.extend(self.tokenize(lines[self.current_line]))
            if tokens[-1] == "/":
                tokens.pop()
                self.current_line += 1
                continue
            self.evaluate_tokens(tokens)
            tokens = []
    def close(self, message=None):
        if message is not None:
            print(message)
        self.running = False
    
    def tokenize(self, line:str) -> list[str]:
        return line.split()
    
    def operate(self, operator:str, stack, tokens):
        return self.registered_operators[operator](self, stack, tokens)
    
    def apply(self, term:str, stack):
        return self.registered_terms[term](self, stack)

        
    
    def parse_token(self, token:str, tokens = []):
        match token:
            case token if token.isdigit():
                return int(token)
            case token if (token.startswith('"') and token.endswith('"')):
                return token.strip('"')
            case token if token.endswith('"'):
                original = token
                while len(tokens) > 0:
                    next_token = tokens.pop()
                    token = next_token.strip('"') + " " + token.strip('"')
                    if next_token.endswith('"'):
                        raise SyntaxError(f"String '{original}' has no beginning on line {self.current_line}")
                    if next_token.startswith('"'):
                        return token
                else:
                    raise SyntaxError(f"String '{original}' has no beginning on line {self.current_line}")
            case token if token.startswith('"'):
                raise SyntaxError(f"string '{token}' has no end on line {self.current_line}")
            case token if (token.startswith('<') and token.endswith('>')):
                return ModuleName(token.strip("<").strip(">"))
            case token if ('.' in token and token != '.'):
                _toks = token.split(".")
                current_token = self.parse_token(_toks.pop())
                for tok in _toks:
                    
                    tokens.append(tok)
                    tokens.append('.')
                return current_token
            case token if token in self.__scope__:
                return self.__scope__[token]
            case token:
                return RawToken(token)
        
    
    def evaluate_tokens(self, tokens:list[str]):
        stack = []
        
        while len(tokens) > 0:
            parsed = self.parse_token(tokens.pop(), tokens)
            
            if isinstance(parsed, RawToken):
                token = parsed.token
                if token in self.registered_operators:
                    if self.operate(token, stack, tokens) == -1:
                        break
                elif token in self.registered_terms:
                    match self.apply(token, stack):
                        case -1:
                            break
                        
                else:
                    stack.append(parsed)
            else:
                stack.append(parsed)
        self.current_line += 1
        return stack


