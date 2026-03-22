from . import Extender



__extension__ = Extender()

@__extension__.add_command.use("in")
def get_input(core, view, stack):
    prompt = stack.pull_if(str)
    stack.push(core.interface.get_input(prompt))