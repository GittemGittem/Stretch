from .grammer import make_tree
from .transformer import transformer
from ..structures import Stack
from lark import Lark


def parse(code_string, transformer=transformer):
    tree = make_tree(code_string)
    block = transformer.transform(tree)
    block["__scopes__"] = Stack()
    return block

