from stretch.interpreter import Interpreter
from stretch.view import BlockView
from stretch.core import Core



if __name__ == "__main__":
    
    interpreter = Interpreter()
    core = Core(interpreter)
    
    with open("main.str", 'r') as code_file:
        block = interpreter.parse(code_file.read())
    interpreter.push(BlockView(block))
    
    interpreter.mainloop(core)