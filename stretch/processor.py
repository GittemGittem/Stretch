from .core_types import Stack
from .lang_types import Expression, Op, RawToken, CallBlock, Block, Assign, Dotpath, CallCoreWord
from .core import default_operators, default_precedence, default_core
from .scope_types import Scope, Function, BlockView

class Processor:
    def __init__(self):
        self.core = default_core.copy()
        self.operators = default_operators.copy()
        self.precedence = default_precedence.copy()
        
    def __call__(self, interpreter, scope, statement):
        tokens = Stack(*statement)
        print(statement)
        self.eval_tokens(interpreter, scope, tokens)
        self.evaluate_expressions(interpreter, scope, tokens) # evaluate expressions first

        
        self.save_vars(interpreter, scope, tokens)
        if len(tokens) > 0:
            print(f"Unused tokens {tokens}")
    
    
    def evaluate_expressions(self, interpreter, scope, tokens):
        index = len(tokens) - 1
        while index >= 0:
            if isinstance(tokens[index], Expression):
                tokens.insert(self.eval_expr(interpreter, scope, tokens.pull(index)), index)
            
            index -= 1
    def eval_expr(self, interpreter, scope, expression):
        for l, operation, r in expression.resolve(self.precedence):
            l = self.eval_term(interpreter, scope, l)
            r = self.eval_term(interpreter, scope, r)
            if operation in self.operators:
                return self.operators[operation](l, r)
            else:
                raise SyntaxError(f"There is no operator '{operation}'")
    def eval_tokens(self, interpreter, scope, tokens):
        for index, token in enumerate(tokens):
            tokens.pull(index)
            parsed = self.eval_term(interpreter, scope, token)
            if parsed is not None:
                tokens.insert(parsed, index)
    
    def eval_term(self, interpreter, scope, term):
        if isinstance(term, RawToken):
            if term in scope:
                return scope.get_var(term)
            else:
                raise Exception(f"Variable '{term.literal}' is undefined in {scope}")
        elif isinstance(term, CallCoreWord):
            name = term.name
            args = term.args
            
            for arg in args:
                print(scope.scope.__scope__)
                print(self.eval_term(interpreter, scope, arg))
            
            if name in self.core:
                return self.core[name](interpreter, scope, *args)
        elif isinstance(term, Block):
            return Function(term.params, term.init, term.reg)
        
        elif isinstance(term, CallBlock):
            name = term.name
            if name in scope:
                func = scope.get_var(name)
                interpreter.push_block(func, args = term.args)
            else:
                raise Exception(f"Function '{name.literal}' is undefined in {scope}")

        return term
    
    def save_vars(self, interpreter, scope, tokens):
        index = len(tokens) - 1
        while index >= 0:
            token = tokens[index]
            if isinstance(token, Assign):
                if len(tokens) > index:
                    to = token.to
                    if isinstance(to, RawToken):
                        to = Dotpath(to)
                    if isinstance(to, Dotpath):
                        path_index = 0
                        save_scope = scope
                        while path_index < len(to.chain) - 1:
                            next = RawToken(to.chain[path_index])
                            if next in save_scope:
                                val = save_scope.get_var(next)
                                if isinstance(save_scope.__scope__[next], Scope):
                                    save_scope = val
                                else:
                                    raise SyntaxError(f"Save path {to} slices non scope value at segment {to.chain[path_index]}")
                                    
                            path_index += 1
                        else:
                            tokens.pull(index)
                            save_scope.set_var(RawToken(to.chain[path_index]), tokens.pull(index))
                                                 
                            path_index += 1
                else:
                    raise SyntaxError(f"Expected token to store after {token.to}:")
                    
            
            
            index -= 1
