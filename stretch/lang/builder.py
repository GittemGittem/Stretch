from lark import Transformer, Discard
from struct import Struct
import struct

from .opcodes import STATEMENT, INIT_STATEMENT, BLOCK, INT, STRING, GROUP, STACK, GET, SET, PATH, COMMAND, STACK_COMMAND
from .opcodes import CONSTANT, TRUE, FALSE, NONE, END
from .instructions import make_instruction, make_instructions, size_bytes


class StretchHexBuilder(Transformer):
    def start(self, start):

        if len(start) > 0:
            return start[0]
        return b''
    
    def code(self, code):
        instructions = b''
        for instruction in code:
            instructions += instruction
        return instructions
    
    def access(self, value):
        return make_instruction(PATH, value[0].encode())
    def access_path(self, path):
        return make_instruction(GET, b''.join(path))
    def set_path(self, path):
        return make_instruction(SET, b''.join(path))
        
    
    def block(self, code):
        return make_instruction(BLOCK, b''.join(code))
    
    def group(self, values):
        return make_instruction(GROUP, b''.join(values))
    def stack(self, values):
        return make_instruction(STACK, b''.join(values))
    
    def instructions(self, instructions):
        return instructions
    
    def statement(self, instructions):
        return make_instruction(STATEMENT, b''.join(instructions[0]))
    def init_statement(self, instructions):
        return make_instruction(INIT_STATEMENT, b''.join(instructions[0]))
    
    def command(self, command):
        return make_instruction(COMMAND, make_instruction(STRING, command[0].encode()) + command[1])
    
    def stack_command(self, command):
        return make_instruction(STACK_COMMAND, make_instruction(STRING, command[0].encode()))
    
    def value(self, val):
        return val[0]
    
    def atom(self, atom):
        return atom[0]
    def NUM(self, num):
        return num[:]
    def INT(self, num):
        num = int(num)
        return make_instruction(INT, num.to_bytes(size_bytes(num)))
    def RAWNUM(self, num):
        return num
    def STR(self, string:str):
        string = string[1:-1].encode()
        return make_instruction(STRING, string)
    
    def constant(self, constant):
        return make_instruction(CONSTANT, constant[0])
    def TRUE(self, true):
        return make_instruction(TRUE)
    def FALSE(self, false):
        return FALSE
    def NONE(self, none):
        return NONE
    def END(self, end):
        return END
    
    def WS(self, ws):
        return Discard
                
        

stretch_builder = StretchHexBuilder()

    
    