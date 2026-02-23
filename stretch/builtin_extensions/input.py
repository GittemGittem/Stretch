
from stretch.extension import Extender

__extensions__ = Extender()
with __extensions__ as extend:
    @extend.term.use("in")
    def get_input(proc, scope, tokens):
        message = ""
        if len(tokens) > 0:
            message = tokens.pop(0)
        if message != "":
            message += "\n"
        tokens.insert(0, input(message))
        return tokens
    