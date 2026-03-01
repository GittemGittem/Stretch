from .lang import Dotpath
def run_stretch(path):
    path = Dotpath(*path.split('.'))
    
    from stretch.parser import parser
    from stretch.interpreter import Interpreter

    interpreter = Interpreter()

    with open(path.file('str'), 'r') as test_file:
        main = parser.parse(test_file.read())
        
        interpreter.process_scope(main)
        interpreter.init_scope(main) # because of how scopes are added, must init second in this case

    interpreter.mainloop()