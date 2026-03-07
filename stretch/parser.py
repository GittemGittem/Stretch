from lark import Lark
from .lang.grammer import stretch_grammer
from .lang import StretchBuilder

parse = Lark(stretch_grammer, parser="lalr", transformer=StretchBuilder()).parse