import sys
from . import run_stretch

def run():
    if len(sys.argv) > 1:
        run_stretch(sys.argv[1])
    else:
        print("Please enter the name of a stretch file to interpret it.")