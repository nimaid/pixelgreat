import os
import sys
import argparse
from enum import Enum
from PIL import Image

from .constants import Direction, DESCRIPTION
from . import helpers
from . import filter

# ---- MAIN CLASSES ----


class LcdPixelate:
    def __init__(self,
                 pixel_width,
                 pixel_height=None,  # Defaults to pixel_width
                 pixel_padding=None,  # Defaults to a reasonable value for the pixel_width and pixel_height
                 pixel_rounding=0.0,
                 pixel_direction=Direction.VERTICAL,
                 filter_strength=1.0,
                 bloom_strength=0.5
                 ):
        self.pixel_width = pixel_width

        if pixel_height is None:
            self.pixel_height = self.pixel_width
        else:
            self.pixel_height = pixel_height

        self.pixel_padding = helpers.clip(pixel_padding, 0, 1)

        self.pixel_rounding = helpers.clip(pixel_rounding, 0, 1)

        self.pixel_direction = pixel_direction

        self.filter_strength = helpers.clip(filter_strength, 0, 1)

        self.bloom_strength = helpers.clip(bloom_strength, 0, 1)


# ---- PROGRAM EXECUTION ----

# Parse arguments
def parse_args(args):
    parser = argparse.ArgumentParser(
        description=f"{DESCRIPTION}\n\nDefault parameters are shown in [brackets].",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    '''
    parser.add_argument("-1", "--first", dest="first_arg", type=float, required=True,
        help="the first argument")
    parser.add_argument("-2", "--second", dest="second_arg", type=float, required=False, default=1.0,
        help="the second argument [1]")
    parser.add_argument("-o", "--operation", dest="opcode", type=str, required=False, default="+",
        help="the operation to perform on the arguments, either \"+\", \"-\", \"*\", or \"/\" [+]")
    '''
    
    return parser.parse_args()


def main(raw_args):
    args = parse_args(raw_args)
    
    print(args)


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
