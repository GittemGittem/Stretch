from .core import Core
from .view import View
from .driver import Driver
from .lang import parse
from .interface import Interface
import sys, os


def load(path):
    if os.path.exists(path):
        with open(path, 'r') as code_file:
            return parse(code_file.read())
    else:
        print(f"File or directory '{path}' not found.")
        return

def run(path = None):
    if path is None:
        
        if len(sys.argv) < 2:
            print("Please add the path to your stretch file!")
            return
        path = sys.argv[1]
    path = "/".join(path.split(".")) + ".str"
            
    block = load(path)
    if block is not None: 
        
        driver = Driver()
        interface = Interface(driver)
        core = Core(interface)
        return driver.mainloop(core, block, interface)


    