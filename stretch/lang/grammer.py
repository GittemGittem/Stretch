stretch_grammer = r"""
    start: statement*
    
    INIT: "$"
    statement: [INIT] (command | value)* ";"
    
    set: var ("." var)* ":"
    get: var ("." var)*
    raw: var "?"
    var: NAME
    
    stat: "|" statement
    block: ("{" statement* "}") # {x: 0; @push @global \stack 7}
    stack: ("[" ( ((value) ("," (value) )*) | statement+)? "]")
    group: ("(" (value ("," value)*)? ")")
    
    call: "<-" group
    getitem: "<-" stack
    
    container: stack | block | group
    
    # the building blocks for information
    atom: NUM
        | STR
        | NONE
        | bool
        
    NONE: "None"
    TRUE: "True"
    FALSE: "False"
    bool: TRUE | FALSE
    
    value: atom | get | container | expr | par_expr | set | raw | stat | call | getitem
    
    OPERATOR: OP+ OP_CHAR* OP* | OP* OP_CHAR* OP+
    
    OP: /[+\-*\/=<>!&%^~]/
    OP_CHAR: /[A-Za-z0-9_]/
    
    par_expr: "(" value (OPERATOR value)+ ")"
    expr: value (OPERATOR value)+

    
    switches: ("@" NAME)*
    command: (NAME switches "->") | ("\\" NAME switches)
    
    COMMENT: /\#[^\n]*/
    %ignore COMMENT
    
    %import common.CNAME -> NAME
    %import common.ESCAPED_STRING -> STR
    %import common.SIGNED_NUMBER -> NUM
    
    %import common.WS
    %ignore WS
"""