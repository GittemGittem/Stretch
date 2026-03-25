from .instructions import fetch_instructions

class ByteRegistry:
    __slots__ = ("next_id", "values")
    def __init__(self):
        self.next_id = 0x00
        self.values = {}
        
        
    @staticmethod
    def is_valid_byte(byte_id:int|bytes):
        match byte_id:
            case byte_id if isinstance(byte_id, int):
                return 0 <= byte_id <= 255
            case byte_id if isinstance(byte_id, bytes):
                if len(byte_id) > 1:
                    return False
                return True
            
            case _:
                raise TypeError(f"Expected a number or byte, not {byte_id}")
    
    def __getitem__(self, byte_id:int|bytes):
        if byte_id in self.values:
            return self.values[byte_id]
        return None

    def __setitem__(self, byte_id:int|bytes, value):
        self.auto(value, byte_id)
    def __contains__(self, byte_id:bytes):
        return byte_id in self.values
    
    def handle(self, process, view, data_bytes):
        virtual_stack = []
        instructions = fetch_instructions(data_bytes)
        for opcode, data in instructions:
            self.values[opcode](process, view, data, virtual_stack)
        
        return virtual_stack
    
    
    def make_id(self, byte_id:int|bytes=None):
        if byte_id is None:
            byte_id = self.next_id
        
        
        if self.is_valid_byte(byte_id):
            if isinstance(byte_id, int):
                self.next_id = byte_id + 1
            else:
                self.next_id = int.from_bytes(byte_id)
            
            
            if isinstance(byte_id, int):
                return byte_id.to_bytes(1)
            else:
                return byte_id
        else:
            raise ValueError(f"Excpected an id within 0 - 255, not {byte_id}")
    
    def auto(self, value=None, byte_id:int|bytes = None):
        id = self.make_id(byte_id)
        
        if value is None:
            if id in self.values:
                del self.values[id]
        else:
            self.values[id] = value
        
        
        return id
    def set(self, byte_id=None):
        def wrap(value=None):
            return self.auto(value, byte_id)
        return wrap
