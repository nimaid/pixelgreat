import os
import sys
import argparse
from enum import Enum
from PIL import Image

from .constants import Direction, ScreenType, DESCRIPTION
from . import helpers
from . import filters


# ---- MAIN CLASSES ----

# The main class that bridges user interaction with the filters
class Pixelgreat:
    def __init_(self,
                size,
                pixel_size,
                screen_type=ScreenType.LCD,
                pixel_padding=None,  # Set default based on screen type
                direction=None,  # Set default based on screen type
                washout=None,  # Set default based on screen type
                blur=None,  # Set default based on screen type
                bloom_size=0.5,
                pixel_aspect=1.0,
                rounding=None,  # Set default based on screen type
                scanline_spacing=0.79,
                scanline_size=0.75,
                scanline_blur=0.25,
                scanline_strength=None,  # Set default based on screen type
                bloom_strength=1.0,
                grid_strength=1.0,
                pixelate=True,
                output_size=None,  # Defaults to input size
                color_mode="RGB"
                ):
        # Get basic settings used for all filters
        helpers.assert_value_in_range(
            size[0],
            minimum=3,
            message="Width must be between {min} and {max} (got {val})"
        )
        helpers.assert_value_in_range(
            size[1],
            minimum=3,
            message="Height must be between {min} and {max} (got {val})"
        )
        self.size = size

        helpers.assert_value_in_range(
            pixel_size,
            minimum=3,
            message="Pixel size must be no less than {min} (got {val})"
        )
        self.pixel_size = pixel_size

        self.screen_type = screen_type

        if pixel_padding is None:
            # Set default based on screen type
            if self.screen_type in [ScreenType.LCD, ScreenType.CRT_TV]:
                self.pixel_padding = 0.25
            else:  # Defaults to CRT monitor
                self.pixel_padding = 0.1
        else:
            helpers.assert_value_in_range(
                pixel_padding,
                minimum=0,
                maximum=1,
                message="Pixel padding must be between {min} and {max} (got {val})"
            )
            self.pixel_padding = pixel_padding

        if direction is None:
            # Set default based on screen type
            if self.screen_type in [ScreenType.LCD, ScreenType.CRT_TV]:
                self.direction = Direction.VERTICAL
            else:  # Defaults to CRT monitor
                self.direction = Direction.HORIZONTAL
        else:
            self.direction = direction

        if washout is None:
            # Set default based on screen type
            if self.screen_type in [ScreenType.CRT_TV, ScreenType.CRT_MONITOR]:
                self.washout = 0.5
            else:  # Defaults to LCD
                self.washout = 0.1
        else:
            helpers.assert_value_in_range(
                washout,
                minimum=0,
                maximum=1,
                message="Washout must be between {min} and {max} (got {val})"
            )
            self.washout = washout

        if blur is None:
            # Set default based on screen type
            if self.screen_type == ScreenType.CRT_TV:
                self.blur = 0.5
            elif self.screen_type == ScreenType.CRT_MONITOR:
                self.blur = 0.75
            else:  # Defaults to LCD
                self.blur = 0
        else:
            helpers.assert_value_in_range(
                blur,
                minimum=0,
                maximum=1,
                message="Blur must be between {min} and {max} (got {val})"
            )
            self.blur = blur

        

        # TODO: Compute actual pixel width based on the desired size and aspect ratio


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

    pass


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
