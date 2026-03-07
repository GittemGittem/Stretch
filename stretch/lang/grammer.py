stretch_grammer = r"""
    start: statement*
    
    INIT: "$"
    statement: [INIT] [set] (command | value)* ";"
    
    set: NAME ":"
    get: (NAME "?") | NAME
    var: NAME
    
    constructor: "<-" NAME
    pair: atom ":" value
    dict: ("{" pair ("," pair)* "}")
    stack: ("{" value ("," value)* "}") # {0, 3, 6, 4}
    block: ("{" statement+ "}") # {x: 0; @push @global \stack 7}
    statement_array: "[" statement+ "]"
    array: ("[" value ("," value)* "]")
    group: ("(" value ("," value)* ")")
    
    cluster: ("<" get ("." get)* ">")
    container: dict | stack | block | array | group | cluster | statement_array | constructor
    
    # the building blocks for information
    atom: NUM
        | STR
    
    value: atom | get | container | expr | par_expr
    
    OPERATOR: OP+ OP_CHAR* OP* | OP* OP_CHAR* OP+
    
    OP: /[+\-*\/=<>!&%^~]/
    OP_CHAR: /[A-Za-z0-9_]/
    
    par_expr: "(" value (OPERATOR value)+ ")"
    expr: value (OPERATOR value)+

    
    switches: ("@" NAME)*
    command: (NAME switches "->") | ("\\" NAME switches)
    
    %import common.CNAME -> NAME
    %import common.ESCAPED_STRING -> STR
    %import common.SIGNED_NUMBER -> NUM
    
    %import common.WS
    %ignore WS
"""