from ..lang.opcodes import instructions, INIT_STATEMENT, STATEMENT, BLOCK
from ..lang.instructions import fetch_instructions
from .machine import View

@instructions.set(BLOCK)
def BLOCK(process, view, data, stack):
    block = {}
    if len(data) > 0:
        block["__instructions__"] = fetch_instructions(data)
        block["__nonlocal__"] = view.block
        process.view_stack.append(View(process, block, {INIT_STATEMENT}))
    stack.append(block)