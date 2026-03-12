from ..extension import Extender
import codecs


__extension__ = Extender()
@__extension__.CommandGroup.use("in")
def get_input(core, view, stack):
    message = stack.pull_if(str) or ""
    stack.push(codecs.decode(input(message), "unicode_escape"))
_print = __extension__.CommandGroup.use("print")(None)

@_print.switch.use("e")
def print_e(core, view, stack):
    print("e")