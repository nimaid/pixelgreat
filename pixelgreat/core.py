import os
import sys
import argparse
import yaml
from enum import Enum

from . import helpers

# ---- MAIN CLASSES ----




# ---- PROGRAM EXECUTION ----

# Parse arguments
def parse_args(args):
    parser = argparse.ArgumentParser(
        description=f"{CONTEXT.DESCRIPTION}\n\nDefault parameters are shown in [brackets].",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("-1", "--first", dest="first_arg", type=float, required=True,
        help="the first argument")
    parser.add_argument("-2", "--second", dest="second_arg", type=float, required=False, default=1.0,
        help="the second argument [1]")
    parser.add_argument("-o", "--operation", dest="opcode", type=str, required=False, default="+",
        help="the operation to perform on the arguments, either \"+\", \"-\", \"*\", or \"/\" [+]")
    
    return parser.parse_args()


def main(raw_args):
    args = parse_args(raw_args)
    
    print(args)


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
