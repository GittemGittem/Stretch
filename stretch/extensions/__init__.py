
from ..commands import commands, add_command

from garnish import garnish

from copy import deepcopy
import importlib

extensions = {}

def __getattr__(path):
    return importlib.import_module("." + path, "stretch.extensions").__extension__

class Extender:
    def __init__(self):
        self.commands = deepcopy(commands)
        
    def extend(self, block:dict):
        block.setdefault("__commands__", {})
        block["__commands__"].update(self.commands)
    
    @garnish
    def add_command(self, func, command_name, *switches):
        add_command.use(command_name, *switches, command_dict = self.commands)(func)
        