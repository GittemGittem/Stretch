from .interpreter import CoreProcessor
from .scope_types import Module, Scope
from .core_types import DotPath, RawToken, Alias, StretchSkipline, StretchTerminate, Stack
import sys

def run_stretch(dot_path):
    processor = CoreProcessor()
    module = Module(processor, DotPath(processor, dot_path))
    processor.run_scope(module)
    
