from .interpreter import Interpreter
from .view import EnterView, InitView
from .core import Core
from sys import argv



def run():
    interpreter = Interpreter()
    core = Core(interpreter)
    
    with open("/".join(argv[1].split(".")) + ".str", 'r') as code_file:
        block = interpreter.parse(code_file.read())
    interpreter.push(EnterView(block))
    interpreter.push(InitView(block))
    
    interpreter.mainloop(core)