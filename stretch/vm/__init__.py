from ..lang.instructions import fetch_instructions

from .machine import VM, Process
from . import handlers

import sys
import os

def run(filename=None):
    if filename is None:
            if len(sys.argv) > 1:
                  filename = sys.argv[1]
            else:
                  print("Please add a stretch file to build!")
                  return
              
    if os.path.exists(filename + '.stb'):
        with open(filename + '.stb', 'rb') as bytecode:
            instructions = fetch_instructions(bytecode.read())
            machine = VM()
            machine.start(Process(instructions))
            for tick in machine:
                pass
            
    else:
        print(f"There is no '{filename}.stb' file")