from lark import Lark, Token, Transformer

from core_types import RawToken, Dotpath
from scope_types import Scope

class StretchBuilder(Transformer):
    def NAME(self, tok):
        return RawToken(tok)
    
    def dotpath(self, items):
        return Dotpath(*[item for item in items if item != '.'])
    
    def block_body(self, block):
        return Scope()




tree_grammer = r"""
INIT: "$"
L_CURL: "{"
R_CURL: "}"
ACCESS: "."
L_PAR: "("
R_PAR: ")"
COLON: ":"
COMMA: ","

start: statement+

statement: init_statement
        | reg_statement
    
init_statement: INIT reg_statement
reg_statement: block_call
            | assign


expr: atom (operator atom)*
atom: dotpath
    | ESCAPED_STRING
    | NAME
operator: "+"
        | "-"
dotpath: NAME ACCESS NAME (ACCESS NAME)* # at least two NAME

assign: NAME COLON expr
    | NAME COLON block_def
block_def: L_PAR [NAME (COMMA NAME)*] R_PAR block_body
block_body: L_CURL statement* R_CURL
block_call: NAME L_PAR [expr (COMMA expr)*] R_PAR

%import common.CNAME -> NAME
%import common.ESCAPED_STRING
%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
"""

test_code = r"""
$path: dot.path
$builtin_block(path)

block: (name) {
    assign: "hello to you" + name
}

$print("hi")
block("meadow", "hi")
"""

parser = Lark(tree_grammer, parser="lalr", lexer="basic", transformer=StretchBuilder())
def get_tokens(code):
    tree = parser.parse(code)
    return list(tree.scan_values(lambda tok:True))

print(get_tokens(test_code))
