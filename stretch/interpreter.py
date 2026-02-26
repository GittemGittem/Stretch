from .core_types import Stack
from .scope_types import BlockView
from .processor import Processor

DEFAULT_PROCESSOR = Processor()

class Interpreter:
    def __init__(self, processor=DEFAULT_PROCESSOR):
        self.running = False
        self.block_stack = Stack()
        
        self.processor = processor
        
    def push_block(self, scope, start=0, args=None):
        if args is None:
            args = ()
        view = BlockView(scope, start)
        view.init(self, Processor, *args)
        self.block_stack.push(view)
    
    def mainloop(self):
        self.running = True
        while self.running:
            if len(self.block_stack) > 1000:
                raise RecursionError()
            block = self.block_stack.peek_if(BlockView)
            if block is None:
                self.running = False
                continue
            
            if not block.step(self):
                self.block_stack.pull()
    
    def process(self, scope, statement):
        self.processor(self, scope, statement)
            