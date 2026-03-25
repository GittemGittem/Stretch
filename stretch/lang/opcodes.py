from .registry import ByteRegistry
import struct
from .instructions import fetch_instruction, fetch_instructions

instructions = ByteRegistry()
# auto returns a unique code for each opcode

# representations of the data each instruction will take
def handle_statement(process, view, instructions, stack):
    stack.clear()
    return instructions

STATEMENT = instructions.auto(handle_statement)
INIT_STATEMENT = instructions.auto(handle_statement)

constants = ByteRegistry()
@instructions.auto
def CONSTANT(process, view, data, stack):
    opcode, data = fetch_instruction(data)
    if opcode == END:
        view.statement.clear()
        return
    stack.append(constants[opcode])
TRUE = constants.auto(True)
FALSE = constants.auto(False)
NONE = constants.auto(None)
END = constants.auto()

BLOCK = instructions.auto()

@instructions.auto
def COMMAND(process, view, data, stack):
    data, arguments = fetch_instructions(data)
    command = data[1]
    result = []
    instructions[arguments[0]](process, view, arguments[1], result)
    arguments = result[0]
    stack.append(arguments)
    print(command, arguments)
@instructions.auto
def STACK_COMMAND(process, view, data, stack):
    command = fetch_instruction(data)[1]
    print(command, stack)

@instructions.auto
def GROUP(process, view, data, stack):
    result = []
    items = fetch_instructions(data)
    while len(items) > 0:
        opcode, value = items.pop()
        if opcode in instructions:
            instructions[opcode](process, view, value, result)
    stack.append(tuple(result[::-1]))
    
@instructions.auto
def STACK(process, view, data, stack):
    result = []
    items = fetch_instructions(data)
    while len(items) > 0:
        opcode, value = items.pop()
        if opcode in instructions:
            instructions[opcode](process, view, value, result)
    stack.append(result[::-1])
            
        

@instructions.auto
def INT(process, view, data, stack):
    stack.append(int.from_bytes(data))

@instructions.auto
def STRING(process, view, data:bytes, stack):
    stack.append(data.decode())
    
PATH = instructions.auto()

@instructions.auto
def GET(process, view, data:bytes, stack):
    where = view.block
    path = fetch_instructions(data)
    for opcode, dest in path[:-1]:
        where = where[dest]
    opcode, final = path[-1]
    stack.append(where[final])
   
@instructions.auto
def SET(process, view, data:bytes, stack):
    where = view.block
    path = fetch_instructions(data)
    for opcode, dest in path[:-1]:
        where = where[dest]
    opcode, final = path[-1]
    where[final] = stack.pop()


OPERATOR = instructions.auto() # similar to string, but handled differently by the vm


