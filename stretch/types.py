class Elif:
    __slots__ = ("condition", "block")
    def __init__(self, block, condition:bool):
        self.block = block
        self.condition = condition