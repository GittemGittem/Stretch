from lark import Lark







stretch_grammer = r"""

start: (code | WS)?

code: (WS? (statement | init_statement) WS? ";" WS?)*

block: "{" (code | WS)? "}"

group: "(" (WS? value (WS value)* WS?)? ")"
stack: "[" WS? value (WS value)* WS? "]"

instructions: value (WS value)*
statement: instructions
init_statement: "$" instructions

access: ("." NAME) | ("\\" RAWNUM)
access_path: access+

set_path: access+ ":"


command: NAME stack # act on the elements in a provided stack
stack_command: NAME WS? "->" # act on the stack

call: access_path (group | stack) # call on the elements in the group or stack provided
# if a stack is provided, it is the only argument \1
# if a group is provided, it is seperated into seperate arguments \0 \1 \2
stack_call: access_path WS? "->" # call on the stack
stack_group_call: access_path WS? "<-" # call on the stack but convert its arguments to a group

value: atom | block | group | stack | access_path | set_path | command | stack_command

atom: INT
    | STR
    | constant

constant: TRUE | FALSE | NONE | END
TRUE: "True"
FALSE: "False"
END: "End"
NONE: "None"

NUM: /[0-9]+/
INT: NUM
RAWNUM: NUM
%import common.ESCAPED_STRING -> STR
%import common.CNAME -> NAME
%import common.WS




"""




make_tree = Lark(stretch_grammer, parser="earley").parse
