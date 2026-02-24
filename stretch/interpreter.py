from .core import __operators__ as core_operators, __terms__ as core_terms, __operator_precedence__ as core_precedence
from .core_types import Stack, DotPath, RawToken, StretchTerminate, StretchSkipline
from .scope_types import Scope, Module
from typing import Generator

class CoreProcessor:
    def __init__(self):
        self.__modules__ = {}
        self.__stack__ = Stack()
        self.running = True
        
        self.__operators__ = core_operators
        self.__terms__ = core_terms
        self.__operator_precedence__ = core_precedence

    def add_module(self, path, module:Module):
        if not isinstance(module, Module):
            raise TypeError(f"processor.add_module() expected a module, not {module.__class__.__name__} '{module}'")
        self.__modules__[path] = module
    
    def modules(self, name=None):
        if name is None:
            return self.__modules__
        return self.__modules__[name]
    
    # STACK
    def stack(self):
        return self.__stack__
    
    def process_line(self, scope:Scope, line):
        try:
            if line.startswith('<'):
                name, line = line.split(':')[:2]
                scope.store(RawToken(name[1:].strip()), line.strip())
            
            else:
                if line.startswith("try"):
                    try:
                        tokens = self.tokenize_line(scope, line[3:])
                        tokens = Stack(*tokens, single_layer=True)
                        self.apply_operators(scope, tokens) # apply scope / module level extension operators first
                        self.apply_operators(scope, tokens) # apply builtin operators
                
                        self.apply_terms(scope, tokens)
                        self.apply_terms(scope, tokens)
            
                        self.save_vars(scope, tokens)
                    except StretchSkipline:
                        pass
                    except StretchTerminate as e:
                        self.stack().push(e)
                    except Exception as e:
                        self.stack().push(StretchTerminate(f"{e}"))
                    
                else:
                    tokens = self.tokenize_line(scope, line)
                    tokens = Stack(*tokens, single_layer=True)
                    
                    self.apply_operators(scope, tokens) # apply scope / module level extension operators first
                    
                    self.apply_terms(scope, tokens)
                
                    self.save_vars(scope, tokens)
        except StretchSkipline:
            pass
            
    def apply_operators(self, scope, tokens):
        operators = scope.operators
        precedence = scope.precedence
        for precedence_group in precedence:
            if any([operator in tokens for operator in precedence_group]):
                index = 0
                while index < len(tokens):
                    if tokens[index] in precedence_group:
                        index -= 1
                        if not index >= 0:
                            try:
                                index += 1
                                op = tokens.pull(index)
                                r = tokens.pull(index)
                                tokens.insert(operators[op](self, scope, r), index)
                                continue
                            except TypeError as e:
                                msg = str(e)
                                if "missing" in msg or "positional argument" in msg:
                                    raise StretchTerminate(f"binary operator '{op.literal}' expected a left side operator")
                                raise StretchTerminate(e)
                            
                        l = tokens.pull(index)
                        op = tokens.pull(index)
                        r = tokens.pull(index)
                        tokens.insert(operators[op](self, scope, l, r), index)
                        continue
                    
                    index += 1
    def apply_terms(self, scope, tokens:Stack): # terms don't have precedence, they are applied right to left on the tokens to their right
        terms = scope.terms
        index = len(tokens) - 1
        while index >= 0:
            token = tokens.peek_if(RawToken, index)
            if token is not None:
                if token in terms:
                    tokens.pull(index)
                    r_toks = tokens[index:]
                    del tokens[index:]
                    
                    terms[token](self, scope, r_toks)
                    
                    tokens.extend(r_toks)
            index -= 1

            
    def save_vars(self, scope, tokens):
        index = len(tokens) - 1
        while index >= 0:
            identifier = tokens.pull_if((RawToken, DotPath), index)
            if identifier is not None:
                if isinstance(identifier, DotPath):
                    name = identifier.end().literal
                    
                    if name.endswith(':'):
                        name = name[:-1]
                        store_in = identifier.scope
                        if store_in is not None:
                            val = tokens.pull(index)
                            store_in.store(name, val)
                        
                elif isinstance(identifier, RawToken):
                    name = identifier.literal
                    if name.endswith(':'):
                        name = name[:-1]
                    name = RawToken(name)
                    if name in scope.operators:
                        raise StretchTerminate(f"Cannot store value in operator {identifier.literal}")
                    elif name in scope.terms:
                        raise StretchTerminate(f"Cannot store value in operator {identifier.literal}")
                    if index > len(tokens):
                        raise StretchTerminate(f"No value to store in {identifier.literal}")
                    val = tokens.pull(index)
                    scope.store(name, val)
            index -= 1
        
    def tokenize_line(self, scope, line):
        tokens = []
        tok_str = []
        start = None
        for chunk in line.split():
            
            if start is None:
                if chunk.startswith('"') and not chunk.endswith('"'):
                    start = '"'
            if start is not None:
                tok_str.append(chunk)
                if chunk.endswith(start):
                    tokens.append(" ".join(tok_str)[1:-1])
                    start = None
            else:
                for tok in self.parse_token(scope, chunk):
                    tokens.append(tok)
        return tokens
      
    def parse_token(self, scope, token:str):
        match token:
            case token if token.isdigit():
                yield int(token)
            case token if token.startswith('-') and token[1:].isdigit():
                yield int(token)
            case token if token.startswith('"') and token.endswith('"'):
                yield token.strip('"')
            case token if token.startswith("'") and token.endswith("'"):
                yield token.strip("'")
            case token if '.' in token:
                split = token.split('.')
                if len(split) == 2 and all([tok.strip('-').isdigit() for tok in split]):
                    yield float(token)
                else:
                    path = DotPath(*split, scope=scope)
                    if len(path.chain) == 1:
                        if not isinstance(path.chain[0], RawToken):
                            yield path.chain.pop()
                        else:
                            yield path
                            
                    else:
                        yield path
                        
            case token:
                raw_token = RawToken(token)
                if scope.contains(raw_token):
                    
                    yield scope.retrieve(raw_token)
                else:
                    yield raw_token
    
    def run_scope(self, scope:Scope):
        self.init_scope(scope)
        self.process_scope(scope)
    
    def init_scope(self, scope:Scope):
        scope.go_to(0)
        
        while scope.current_line < len(scope.__lines__):
            if not self.running:
                break
            
            line = scope.__lines__[scope.current_line]
            while line.endswith(':/'):
                scope.current_line += 1
                line = line[:-2] + " " + scope.__lines__[scope.current_line]

            if line.startswith("$"):
                self.process_line(scope, line[1:])
            scope.current_line += 1
        
    def process_scope(self, scope:Scope, start_line=0):
        
        scope.go_to(start_line)
        
        while scope.current_line < len(scope.__lines__):
            if not self.running:
                break
            line = scope.__lines__[scope.current_line]
            while line.endswith(':/'):
                scope.current_line += 1
                line = line[:-2] + " " + scope.__lines__[scope.current_line]

            if not line.startswith("$"):
                self.process_line(scope, line)
            scope.current_line += 1
    

