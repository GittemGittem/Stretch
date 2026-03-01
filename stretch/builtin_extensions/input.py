from stretch.extension import Extender

__extension__ = Extender()
with __extension__ as e:
    @e.term.use("in")
    def get_input(interpreter, view, tokens):
        message = tokens.pull_if(str) or ""
        tokens.insert(input(message))
    
    @e.term.use("ins")
    def get_input(interpreter, view, tokens):
        sentinal = tokens.pull_only(str)
        message = tokens.pull_if(str) or ""
        result = ""
        inp = input(message)
        while inp != sentinal:
            result += inp.encode().decode()
            inp = input(message)
        tokens.insert(result)