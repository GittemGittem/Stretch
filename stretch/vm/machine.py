
from ..lang.opcodes import instructions, INIT_STATEMENT, STATEMENT
from ..lang.instructions import fetch_instructions

class View:
    def __init__(self, process, block, instruction_set=None):
        self.process = process
        self.block = block
        if instruction_set is None:
            instruction_set = {STATEMENT}
        self.instruction_set = instruction_set
        self.instructions = block.get("__instructions__", [])
        self.current_instruction = 0
        self.statement = []
        self.stack  = []
    
    def tick(self):
        if len(self.statement) <= 0:
            if self.current_instruction >= len(self.instructions):
                return False
            opcode, statement = self.instructions[self.current_instruction]
            if opcode in self.instruction_set:
                if handler := instructions[opcode]:
                    statement = handler(self.process, self, statement, self.stack)
                self.statement = fetch_instructions(statement) # load instructions from statemebytecode
                self.current_instruction += 1
        
        else:
            opcode, data = self.statement.pop()
            if (handler := instructions[opcode]) is not None:
                handler(self.process, self, data, self.stack)

        
        
        return True
    
    @property
    def next(self):
        return self.instructions[self.current_instruction]

class Process:
    def __init__(self, instructions):
        self.main = {"__instructions__":instructions}
        self.view_stack = [View(self, self.main)]
    def tick(self):
        current = self.current
        if current:
            if not current.tick():
                self.view_stack.pop()
            return True
        else:
            return False    

    @property
    def current(self):
        if len(self.view_stack) > 0:
            return self.view_stack[0]
        else:
            return None

class VM:
    def __init__(self):
        self.running = False
        self.processes = []
    def start(self, process:Process):
        self.processes.append(process)
        
    def __iter__(self):
        while len(self.processes) > 0:
            if not (tick_value := self.current.tick()):
                self.processes.pop()
            yield tick_value
                
    @property
    def current(self):
        if len(self.processes) > 0:
            return self.processes[0]
        return None