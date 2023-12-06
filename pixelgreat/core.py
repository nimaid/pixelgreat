import os
import sys
import argparse
import warnings
from enum import Enum
from PIL import Image

from .constants import Direction, ScreenType, DESCRIPTION
from . import helpers
from . import filters


# ---- MAIN CLASSES ----

# The main class that safely bridges user interaction with the filters
class Pixelgreat:
    def __init__(self,
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
        if pixel_size < 10:
            warnings.warn("Pixel sizes below 10 may cause visual glitches. "
                          "Instead of making the pixels smaller, try making the output size larger.")
        self.pixel_size = pixel_size

        if not isinstance(screen_type, ScreenType):
            raise ValueError("The screen_type argument must be a valid ScreenType instance")
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
                message="Blur amount must be between {min} and {max} (got {val})"
            )
            self.blur = blur

        helpers.assert_value_in_range(
            bloom_size,
            minimum=0,
            maximum=1,
            message="Bloom size must be between {min} and {max} (got {val})"
        )
        self.bloom_size = bloom_size

        helpers.assert_value_in_range(
            pixel_aspect,
            minimum=0.33,
            maximum=3,
            message="Pixel aspect ratio must be between {min} and {max} (got {val})"
        )
        self.pixel_aspect = pixel_aspect

        if rounding is None:
            # Set default based on screen type
            if self.screen_type == ScreenType.CRT_TV:
                self.rounding = 0.5
            else:  # Rounded pixels only apply to the CRT TV
                self.rounding = 0
        else:
            helpers.assert_value_in_range(
                rounding,
                minimum=0,
                maximum=1,
                message="Rounding must be between {min} and {max} (got {val})"
            )
            self.rounding = rounding

        helpers.assert_value_in_range(
            scanline_spacing,
            minimum=0.33,
            maximum=3,
            message="Scanline spacing must be between {min} and {max} (got {val})"
        )
        self.scanline_spacing = scanline_spacing

        helpers.assert_value_in_range(
            scanline_size,
            minimum=0,
            maximum=1,
            message="Scanline size must be between {min} and {max} (got {val})"
        )
        self.scanline_size = scanline_size

        helpers.assert_value_in_range(
            scanline_blur,
            minimum=0,
            maximum=1,
            message="Scanline blur must be between {min} and {max} (got {val})"
        )
        self.scanline_blur = scanline_blur

        if scanline_strength is None:
            # Set default based on screen type
            if self.screen_type in [ScreenType.CRT_TV, ScreenType.CRT_MONITOR]:
                self.scanline_strength = 1
            else:  # Defaults to LCD
                self.scanline_strength = 0
        else:
            helpers.assert_value_in_range(
                scanline_strength,
                minimum=0,
                maximum=1,
                message="Scanline strength must be between {min} and {max} (got {val})"
            )
            self.scanline_strength = scanline_strength

        helpers.assert_value_in_range(
            bloom_strength,
            minimum=0,
            maximum=1,
            message="Bloom strength must be between {min} and {max} (got {val})"
        )
        self.bloom_strength = bloom_strength

        helpers.assert_value_in_range(
            grid_strength,
            minimum=0,
            maximum=1,
            message="Grid strength must be between {min} and {max} (got {val})"
        )
        self.grid_strength = grid_strength

        if not isinstance(pixelate, bool):
            raise ValueError("The pixelate argument must be a valid boolean value")
        self.pixelate = pixelate

        if output_size is None:
            # Defaults to input size
            self.output_size = self.size
        else:
            helpers.assert_value_in_range(
                output_size[0],
                minimum=3,
                message="Output width must be no less than {min} (got {val})"
            )
            helpers.assert_value_in_range(
                output_size[1],
                minimum=3,
                message="Output height must be no less than {min} (got {val})"
            )
            self.output_size = output_size

        color_mode = color_mode.upper()
        if "R" in color_mode and "G" in color_mode and "B" in color_mode:
            self.color_mode = color_mode
        else:
            raise ValueError(f"The color mode must have a red channel, "
                             f"a green channel, and a blue channel (got {color_mode})")

        # Compute actual pixel width based on the desired size of the smallest side
        if pixel_aspect > 1:
            # Wider than tall, use as height (to compute width)
            self.pixel_width = round(self.pixel_size * self.pixel_aspect)
        else:
            # Taller than wide, use as width
            self.pixel_width = round(self.pixel_size)

        # Create the composite filter object with the selected settings
        self.filter = filters.CompositeFilter(
            size=self.size,
            screen_type=self.screen_type,
            pixel_width=self.pixel_width,
            pixel_padding=self.pixel_padding,
            direction=self.direction,
            washout=self.washout,
            blur=self.blur,
            bloom_size=self.bloom_size,
            pixel_aspect=self.pixel_aspect,
            rounding=self.rounding,
            scanline_spacing=self.scanline_spacing,
            scanline_size=self.scanline_size,
            scanline_blur=self.scanline_blur,
            scanline_strength=self.scanline_strength,
            bloom_strength=self.bloom_strength,
            grid_strength=self.grid_strength,
            pixelate=self.pixelate,
            output_size=self.output_size,
            color_mode=self.color_mode
        )

    def apply(self, image):
        result = self.filter.apply(image)

        return result

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
    # TODO: Add command line functionality
    print("Hello, world!")
    pass


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
