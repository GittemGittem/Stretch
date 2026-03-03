from lark import Transformer, Lark
from .lang import SetVar, RawToken, Op, Statement, Expression, Block, Dotpath, Pointer, Command, Switch, Dummy
import codecs

class StretchBuilder(Transformer):
    def start(self, code):
        init_statements = {}
        statements = {}
        line = 0
        for stat, init in [st for st in code if st is not None]:
            if init:
                init_statements[line] = stat
            else:
                statements[line] = stat
            line += 1
        return Block(statements, init_statements, line)
    def statement(self, stat):
        return [part for part in stat if part is not None], False
    def init_statement(self, stat):
        return [part for part in stat if part is not None], True
    def section(self, section):
        return section
    def part(self, pt):
        return pt[0]
    
    def NEWLINE(self, nwl):
        return None
    def l_brack(self, brack):
        return None
    def r_brack(self, brack):
        return None    
    
    def init(self, init):
        return None
    def COMMA(self, comma):
        return None
    def semi(self, semi):
        return None
    

    def atom(self, atom):
        return atom[0]
    def term(self, term):
        while isinstance(term, list):
            term = term[0]
        return term
    def par_term(self, term):
        return term[1:-1]
    def expr(self, expr):
        if len(expr) == 1:
            return expr[0]
        return Expression(expr)
    
    def block(self, block):
        return block[1]

    
    def STRING(self, str_tok):
        inner = str_tok[1:-1] # remove quotes return
        return codecs.decode(inner, "unicode_escape")
    def string_content(self, content):
        return content
    def STRING_TEXT(self, text):
        return str(text)
    def brace_group(self, group):
        if isinstance(group[0], list):
            group = group[0]
        return '"' + "".join(group) + '"'
    def brack_group(self, group):
        if isinstance(group[0], list):
            group = group[0]
        return "'" + "".join(group) + "'"
    
    def NUM(self, num_tok):
        return float(num_tok) if '.' in num_tok else int(num_tok)
    def NAME(self, token):
        return RawToken(str(token))
    def access(self, acc):
        return None
    def MARK(self, mark):
        return True
    
    
    def switch(self, switch):
        return Switch(switch[0])
    def command(self, cmd):
        return Command(cmd[-1].literal, *[switch.literal for switch in cmd[:-1] if switch is not None])
    
    def name(self, path):
        if len(path) > 1:
            return Dotpath(*[seg.literal for seg in path if seg is not None])
        return path[0]
    def pointer(self, point):
        mark, reference = point
        return Pointer(reference, mark or False)
    
    def dummy(self, dummy):
        return Dummy(dummy[0])
    
    OPERATOR = Op
    def set(self, set_tok):
        return SetVar(set_tok[0])
    def group(self, group):
        return tuple([item for item in group if item is not None])
        

grammar = r"""
    
    
    OPERATOR: OP+ OP_CHAR* OP* | OP* OP_CHAR* OP+
    
    OP: /[+\-*\/=<>!&%^~]/
    OP_CHAR: /[A-Za-z0-9_]/

    colon : ":"
    semi : ";"
    access : "."
    l_access : "<"
    r_access : ">"
    init : "$"
    l_par : "("
    r_par : ")"
    COMMA : ","
    l_brack : "{"
    r_brack : "}"
    MARK : "@"
        
    start: (statement semi | init_statement semi)*
    statement: [set] expr+
    init_statement: init [set] expr+
    set: (name | group) ":"
    
    block: l_brack start r_brack
    
    newline: NEWLINE*
    
    atom: STRING
    | NUM
    | name
    | command
    | pointer
    | block
    | group
    | dummy
    
    dummy: "<-" expr
    
    switch:  "@" NAME
    command: switch* (("(" NAME ")") | (NAME "->"))
    
    group: atom (COMMA atom)+

    par_term: (l_par expr r_par)
    term: atom
    | par_term
    expr: term (OPERATOR term)*
    
    pointer: "[" [MARK] expr "]"
    name: NAME (access NAME)*
    
    COMMENT: /\#[^\n]*/
    %ignore COMMENT
    %import common.NEWLINE
    %import common.CNAME -> NAME
    %import common.ESCAPED_STRING -> STRING

    %import common.SIGNED_NUMBER -> NUM
    
    %import common.WS
    %ignore WS


"""

parser = Lark(grammar, parser="lalr", transformer=StretchBuilder())
