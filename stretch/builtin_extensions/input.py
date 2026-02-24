
from stretch.extension import Extender

__extensions__ = Extender()
with __extensions__ as extend:
    @extend.term.use("in")
    def get_input(proc, scope, tokens):
        message = tokens.pull_if(str)
        if message is None:
            message = ""
        message = message.encode("utf-8").decode("unicode_escape")  
        tokens.insert(input(message))
    @extend.term.use("ins")
    def get_input(proc, scope, tokens):
        message = tokens.pull_if(str)
        if message is None:
            message = ""
        message = message.encode("utf-8").decode("unicode_escape")
        user_input = "/"
        while user_input.endswith("/"):
            user_input = user_input[:-1]
            user_input += input(message)
        tokens.insert(user_input)
    