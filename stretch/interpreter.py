from .core import __operators__ as core_operators, __terms__ as core_terms
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
        self.__types__ = {}

    def add_module(self, module:Module):
        if not isinstance(module, Module):
            raise TypeError(f"processor.add_module() expected a module, not {module.__class__.__name__} '{module}'")
        self.__modules__[module.name] = module
    
    def modules(self, name=None):
        if name is None:
            return self.__modules__
        return self.__modules__[name]
    
    # STACK
    def stack(self):
        return self.__stack__
    
    def process_line(self, scope:Scope, line):
        try:
            tokens = Stack(*self.tokenize_line(scope, line), single_layer=True)
            
            self.apply_operators(scope, scope.operators(), tokens) # apply scope / module level extension operators first
            self.apply_operators(scope, self.__operators__, tokens) # apply builtin operators
            
            self.apply_terms(scope, scope.terms(), tokens)
            self.apply_terms(scope, self.__terms__, tokens)
            
            self.save_vars(scope, tokens)
        except StretchSkipline:
            pass
            
    def apply_operators(self, scope, operators, tokens):
        for operator in operators:
            while operator in tokens:
                index = tokens.index(operator) - 1
                l = tokens.pull(index)
                _ = tokens.pull(index)
                r = tokens.pull(index)
                result = operators[operator](self, scope, l, r) # an operator operates on the tokens to its left and to its right, and has access to the processor
                if result is not None:
                    tokens.insert(index, result)
    def apply_terms(self, scope, terms, tokens:Stack): # terms don't have precedence, they are applied right to left on the tokens to their right
        index = len(tokens) - 1
        while index >= 0:
            token = tokens.peek_if(index, RawToken)
            if token is not None:
                if token in terms:
                    tokens.pull(index)
                    r_toks = tokens[index:]
                    del tokens[index:]
                    
                    remaining = terms[token](self, scope, r_toks)
                    if remaining is None:
                        remaining = Stack(single_layer=True)
                    elif not isinstance(remaining, (Stack, list, tuple)):
                        remaining = Stack(remaining, single_layer=True)
                    tokens.extend(remaining)
            index -= 1

            
    def save_vars(self, scope, tokens):
        index = len(tokens) - 1
        while index >= 0:
            token = tokens.peek_if(index, RawToken)
            if token is not None:
                if token.literal.endswith(":"):
                    name = RawToken(token.literal[:-1])
                    tokens.pop(index)
                    if index > len(tokens):
                        raise StretchTerminate(f"attempt to store {name} recieved no value")
                    value = tokens.pop(index)
                    scope.store(name, value)
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
                for token in self.tokenize(chunk):
                    tokens.append(self.parse_token(scope, token))
        return tokens
    
    def tokenize(self, chunk):
        tokens = []
        for tok in chunk.split('.'):
            tokens.append(tok)
            tokens.append('.')
        else:
            tokens.pop()
        for token in tokens:
            yield token
            
    def parse_token(self, scope, token:str):
        match token:
            case token if token.isdigit():
                return int(token)
            case token if token.startswith('-') and token[1:].isdigit():
                return int(token)
            case token if token.startswith('"') and token.endswith('"'):
                return token.strip('"')
            case token if token.startswith("'") and token.endswith("'"):
                return token.strip("'")
            case token:
                raw_token = RawToken(token)
                if scope.contains(raw_token):
                    
                    return scope.retrieve(raw_token)
                return raw_token
    
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
    

