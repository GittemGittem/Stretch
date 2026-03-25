import struct

# storing instructions

# store opcode and length and then value
def make_instruction(opcode:bytes, data:bytes=None) -> bytes:
    if data is None:
        data = b''
    length = len(data)
    
    return opcode + length.to_bytes(2) + data

# store multiple instructions
def make_instructions(*instructions:tuple[bytes, bytes]) -> bytes:
    binary = bytearray()
    for opcode, data in instructions:
        binary += make_instruction(opcode, data)
    return bytes(binary)


# retreiving instructions
# only use if you know its a single instruction
def fetch_instruction(binary_bytecode:bytes) -> tuple[bytes, bytes]:
    opcode = binary_bytecode[:1]
    length = int.from_bytes(binary_bytecode[1:3])
    return (opcode, binary_bytecode[3:3+length])

def fetch_instructions(binary_bytecode:bytes) -> list[tuple[bytes, bytes]]:
    # documenting a lot here because this is a lot
    # when you haven't used binary very much
    instructions = [] # the list of instructions to return
    index = 0
    while index < len(binary_bytecode):
        # each instructions 'header' is 3 bytes
        # an opcode (1 byte), and the size of its data (2 bytes)
        opcode, data_length = binary_bytecode[index:index + 1], binary_bytecode[index + 1:index + 3]
        data_length = int.from_bytes(data_length)
        index += 3
        
        # use the data length to get the full value
        value = binary_bytecode[index:index + data_length]
        index += data_length
        # add the instruction and its value to be returned
        instructions.append((opcode, value))
    return instructions


def size_bytes(val:int):
    n = 0
    while val != 0:
        val >>= 8
        n += 1
    return n