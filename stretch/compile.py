from .lang import build
import sys

def compile(filename=None):
      
      if filename is None:
            if len(sys.argv) > 1:
                  filename = sys.argv[1]
            else:
                  print("Please add a stretch file to build!")
                  return
            
      with open(filename + '.str', 'r') as stretch_file:
            bytecode = build(stretch_file.read())

      with open(filename + '.stb', 'wb') as stb:
            stb.write(bytecode)



