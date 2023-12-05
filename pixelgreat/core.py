import os
import sys
import argparse
from enum import Enum
from PIL import Image

from .constants import Direction, ScreenType, DESCRIPTION
from . import helpers
from . import filters


# ---- MAIN CLASSES ----


class LcdPixelate:
    def __init__(self,
                 pixel_size,
                 pixel_aspect=1.0,
                 pixel_padding=0.25,
                 pixel_rounding=0.25,
                 pixel_direction=Direction.VERTICAL,
                 overlay_only=False,
                 blur=0.0,
                 blur_ratio=1.0,
                 filter_strength=1.0,
                 bloom_strength=0.5
                 ):
        if pixel_size < 3:
            raise ValueError("Pixel size must be at least 3")
        self.pixel_size = pixel_size

        self.pixel_aspect = max(abs(pixel_aspect), 0.01)

        self.pixel_padding = helpers.clip(pixel_padding, 0, 1)

        self.pixel_rounding = helpers.clip(pixel_rounding, 0, 1)

        self.overlay_only = overlay_only

        self.pixel_direction = pixel_direction

        self.blur = helpers.clip(blur, 0, 1)

        self.blur_ratio = helpers.clip(blur_ratio, 0, 1)

        self.filter_strength = helpers.clip(filter_strength, 0, 1)

        self.bloom_strength = helpers.clip(bloom_strength, 0, 1)

    def process(self, image):
        pass


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

    test = LcdPixelate(6)
    test.process("Wow")


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
