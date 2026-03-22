
from lark import Lark

stretch_grammer = r"""
start: code

code: (statement | init_statement | WS)*

container: block | stack | group
block: "{" code "}"
stack: "[" WS? (value WS? ("," WS? value WS?)*)? "]"
group: "(" WS? (value WS? ("," WS? value WS?)*)? ")"

call: value group
getitem: value stack

init_statement: "$" WS? statement
statement: value (WS value)* WS? ";"

var: (NAME | ("\\" NUM)) (("." NAME | ("\\" NUM)))*
set: var WS? ":"
get: var WS?

value: atom
    | container
    | set
    | get
    | call
    | getitem
    | command
    | expression
    
command: (NAME (WS switches)? WS? "->") | ("<" NAME WS? switches? WS? ">")
switches: "@" NAME ("\\" NAME)*

OPERATOR: OP+ OP_CHAR* OP* | OP* OP_CHAR* OP+
    
OP: /(?!->)[+\-*\/=<>!&%^~]/

OP_CHAR: /[A-Za-z0-9_]/

expression: par_expr | expr
par_expr: "(" value WS? (OPERATOR WS? value)+ ")"
expr: value WS? (OPERATOR WS? value)+



TRUE.0: "True"
FALSE.0: "False"

atom: NUM
    | str
    | TRUE
    | FALSE
    
str: STR
    | var "?"
    
COMMENT: /\#[^\n]*/
%ignore COMMENT

%import common.SIGNED_NUMBER -> NUM
%import common.ESCAPED_STRING -> STR
%import common.CNAME -> NAME


%import common.WS
"""
make_tree = Lark(stretch_grammer, parser="earley").parse