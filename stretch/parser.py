from lark import Transformer, Lark
from .lang_types import Op, RawToken, Dotpath, Expression, Block, Assign, CallBlock, CallCoreWord, Coreword

class StretchBuilder(Transformer):
    
    OPERATOR = Op
    NAME = RawToken
    
    COMMA = Op
    
    def dotpath(self, path):
        return Dotpath(*[seg for seg in path if isinstance(seg, RawToken)])
    
    def start(self, statements):
        return statements
    def use_coreword(self, cwst):
        name = Coreword(cwst[0])
        args = tuple(arg for arg in cwst[2].children if not isinstance(arg, Op))
        return [CallCoreWord(name, args)]

    
    def reg_statement(self, stat):
        return stat[0], "regular"
    def init_statement(self, stat):
        return stat[1][0], "init"
    def statement(self, stat):
        return stat[0]
    
    def atom(self, atom):
        return atom[0]
    def par_term(self, exp):
        return Expression(exp[1:-1])
    def term(self, term):
        return term[0]
    def expr(self, exp):
        return Expression(exp)
    
    def STRING(self, text):
        return text[1:-1].encode("utf-8").decode()
    def NUM(self, number):
        if '.' in number:
            return float(number)
        else:
            return int(number)
    def block(self, block):
        return Block(block[1:-1])
    def params(self, params):
        return tuple(param for param in params if isinstance(param, RawToken) and not isinstance(param, Op))
    def args(self, args):
        return tuple(arg for arg in args if not isinstance(arg, Op))[1:-1]
    def def_block(self, block):
        params = block[0]
        code = block[-1]
        code.params = params
        return code
    def call_block(self, block):
        name = block[0]
        args = block[1]
        return [CallBlock(name, args)]
    
    def assign(self, assignment):
        return [Assign(assignment[0]), *assignment[2:]]
        
        

grammar = r"""
    OPERATOR: OP OP_CHAR* | OP_CHAR* OP
    
    OP: /[+\-*\/=<>!&%^~]/
    OP_CHAR: /[A-Za-z0-9_]/

    COLON : ":"
    access : "."
    l_access : "<"
    r_access : ">"
    init : "$"
    l_par : "("
    r_par : ")"
    COMMA : ","
    l_brack : "{"
    r_brack : "}"
    semi : ";"
    CORE : "|"
        
    start: (statement (semi statement)*)+
    statement: reg_statement
            | init_statement
    reg_statement: assign
                | call_block
                | use_coreword
    init_statement: init reg_statement
    
    atom: NAME
    | dotpath
    | STRING
    | NUM
    | call_block

    par_term: (l_par expr r_par)

    term: atom
    | par_term

    expr: term (OPERATOR term)*
    
    params: l_par [NAME (COMMA NAME)*] r_par
    def_block: params block
    block: l_brack statement* r_brack
    args: l_par [(expr | block | def_block) (COMMA (expr | block | def_block))*] r_par
    call_block: (NAME|dotpath) args
    
    assign: (NAME | dotpath) COLON (expr | def_block | block)
        | (NAME | dotpath) COLON use_coreword
    
    dotpath: NAME access NAME (access NAME)*
    core_args : (expr | block | def_block) (COMMA (expr | block | def_block))*
    use_coreword : NAME CORE core_args CORE
    %import common.CNAME -> NAME
    %import common.ESCAPED_STRING -> STRING
    %import common.SIGNED_NUMBER -> NUM
    
    %import common.WS
    %ignore WS

"""

parser = Lark(grammar, parser="lalr", transformer=StretchBuilder())
