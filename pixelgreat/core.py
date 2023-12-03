import os
import sys
import argparse
import yaml
from enum import Enum

from . import helpers

# ---- MAIN CLASSES ----

# Main class
class Python3Template:
    def __init__(self,
                 first,
                 second,
                 opcode
                 ):
        self.first = first
        self.second = second
        self.opcode = opcode.strip()
        
        if self.opcode not in self.OpCodes.VALID_OPTIONS.value:
            raise argparse.ArgumentTypeError("The operation code must be either \"+\", \"-\", \"*\", or \"/\"")
        if self.opcode == self.OpCodes.DIV.value and self.second == 0:
            raise ZeroDivisionError("Cannot divide by zero!")

    class OpCodes(Enum):
        ADD = "+"
        SUB = "-"
        MULT = "*"
        DIV = "/"
        VALID_OPTIONS = "+-*/"
    
    def add(self):
        return self.first + self.second
    
    def sub(self):
        return self.first - self.second
    
    def mult(self):
        return self.first * self.second
    
    def div(self):
        return self.first / self.second
    
    def operate(self):
        if self.opcode == self.OpCodes.ADD.value:
            print(f"The equation is {self.first} + {self.second}")
            return self.add()
        elif self.opcode == self.OpCodes.SUB.value:
            print(f"The equation is {self.first} - {self.second}")
            return self.sub()
        elif self.opcode == self.OpCodes.MULT.value:
            print(f"The equation is {self.first} * {self.second}")
            return self.mult()
        elif self.opcode == self.OpCodes.DIV.value:
            print(f"The equation is {self.first} / {self.second}")
            return self.div()
        else:
            raise argparse.ArgumentTypeError(f"Invalid opcode: \"{self.opcode}\"")
    
    def run(self):
        result = self.operate()
        print(f"The answer is {result}")


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


def main(args):
    args = parse_args(args)
    
    python_3_template = Python3Template(
        first=args.first_arg, 
        second=args.second_arg, 
        opcode=args.opcode)
    
    python_3_template.run()


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
