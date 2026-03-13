from garnish import garnish
from copy import deepcopy
from .commands import commands
from .operators import operators, precedence

class Group(tuple):
    def __repr__(self):
        return f"({", ".join(str(value) for value in self)})"
    def dot(self):
        return ".".join(self)


class Stack(list):
    def push(self, value):
        list.insert(self, 0, value)
    def pull(self, index=0):
        return self.pop(0)
    def peek(self, index=0):
        if index < len(self):  
            return self[index]
        return None
    def peek_if(self, type, index=0):
        if index < len(self):
            if isinstance(self.peek(index), type): 
                return self[index]
        return None
    def pull_if(self, type):
        if len(self) > 0:
            if isinstance(self[0], type):
                return self.pull()
        return None
    def pull_only(self, type):
        if len(self) > 0:
            if isinstance(self[0], type):
                return self.pull()
        raise TypeError()
    
    def insert(self, value, index=0):
        list.insert(self, index, value)
        
    def __repr__(self):
        return f"[{", ".join([str(item) for item in self])}]"
    dot = Group.dot

class Promise(Stack):
    def __init__(self, owner):
        self.owner = owner

class Block(dict):
    def __new__(cls, *args):
        instance = super().__new__(cls, *args)
        instance["promise"] = Promise(instance)
        return instance
    
    @property
    def stats(self):
        return self.get("statements", Stack())
    @property
    def commands(self):
        return self.get("commands", commands)
    @property
    def operators(self):
        return self.get("operators", operators)
    @property
    def precedence(self):
        return self.get("precedence", precedence)
    @property
    def call(self):
        return self.get("__call__", None)
    @property
    def promise(self):
        return self["promise"]

class Statement:
    __slots__ = ("parts", "init")
    def __init__(self, statement = [], init=False):
        self.parts = statement
        self.init = init
    def __repr__(self):
        return f"{" ".join(str(part) if not isinstance(part, str) else f'"{part}"' for part in self.parts)};"