import os
import sys
import argparse
import warnings
from enum import Enum
from PIL import Image

from .constants import Direction, ScreenType, DESCRIPTION
from . import helpers
from . import filters


# ---- MAIN CLASSES AND FUNCTIONS ----

# The main reusable class that safely bridges user interaction with the filters
class Pixelgreat:
    def __init__(self,
                 size,
                 pixel_size,
                 screen_type=None,  # Set to a static default
                 pixel_padding=None,  # Set default based on screen type
                 direction=None,  # Set default based on screen type
                 washout=None,  # Set default based on screen type
                 blur=None,  # Set default based on screen type
                 bloom_size=None,  # Set to a static default
                 pixel_aspect=None,  # Set to a static default
                 rounding=None,  # Set default based on screen type
                 scanline_spacing=None,  # Set to a static default
                 scanline_size=None,  # Set to a static default
                 scanline_blur=None,  # Set to a static default
                 scanline_strength=None,  # Set default based on screen type
                 bloom_strength=None,  # Set to a static default
                 grid_strength=None,  # Set to a static default
                 pixelate=None,  # Set to a static default
                 output_scale=None,  # Set to a static default
                 color_mode=None  # Set to a static default
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

        if screen_type is None:
            screen_type = ScreenType.LCD
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

        if bloom_size is None:
            bloom_size = 0.5
        helpers.assert_value_in_range(
            bloom_size,
            minimum=0,
            maximum=1,
            message="Bloom size must be between {min} and {max} (got {val})"
        )
        self.bloom_size = bloom_size

        if pixel_aspect is None:
            pixel_aspect = 1.0
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

        if scanline_spacing is None:
            scanline_spacing = 0.79
        helpers.assert_value_in_range(
            scanline_spacing,
            minimum=0.33,
            maximum=3,
            message="Scanline spacing must be between {min} and {max} (got {val})"
        )
        self.scanline_spacing = scanline_spacing

        if scanline_size is None:
            scanline_size = 0.75
        helpers.assert_value_in_range(
            scanline_size,
            minimum=0,
            maximum=1,
            message="Scanline size must be between {min} and {max} (got {val})"
        )
        self.scanline_size = scanline_size

        if scanline_blur is None:
            scanline_blur = 0.25
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

        if bloom_strength is None:
            bloom_strength = 1.0
        helpers.assert_value_in_range(
            bloom_strength,
            minimum=0,
            maximum=1,
            message="Bloom strength must be between {min} and {max} (got {val})"
        )
        self.bloom_strength = bloom_strength

        if grid_strength is None:
            grid_strength = 1.0
        helpers.assert_value_in_range(
            grid_strength,
            minimum=0,
            maximum=1,
            message="Grid strength must be between {min} and {max} (got {val})"
        )
        self.grid_strength = grid_strength

        if pixelate is None:
            pixelate = True
        if not isinstance(pixelate, bool):
            raise ValueError("The pixelate argument must be a valid boolean value")
        self.pixelate = pixelate

        if output_scale is None:
            output_scale = 1.0
        helpers.assert_value_in_range(
            output_scale,
            minimum=0.1,
            message="Output scale must be no less than {min} (got {val})"
        )
        self.output_size = (
                round(self.size[0] * output_scale),
                round(self.size[1] * output_scale)
        )

        if color_mode is None:
            color_mode = "RGB"
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


# A single use helper function
def pixelgreat(image,
               pixel_size,
               screen_type=None,
               pixel_padding=None,
               direction=None,
               washout=None,
               blur=None,
               bloom_size=None,
               pixel_aspect=None,
               rounding=None,
               scanline_spacing=None,
               scanline_size=None,
               scanline_blur=None,
               scanline_strength=None,
               bloom_strength=None,
               grid_strength=None,
               pixelate=None,
               output_scale=None
               ):
    pg_object = Pixelgreat(
        size=image.size,
        pixel_size=pixel_size,
        screen_type=screen_type,
        pixel_padding=pixel_padding,
        direction=direction,
        washout=washout,
        blur=blur,
        bloom_size=bloom_size,
        pixel_aspect=pixel_aspect,
        rounding=rounding,
        scanline_spacing=scanline_spacing,
        scanline_size=scanline_size,
        scanline_blur=scanline_blur,
        scanline_strength=scanline_strength,
        bloom_strength=bloom_strength,
        grid_strength=grid_strength,
        pixelate=pixelate,
        output_scale=output_scale,
        color_mode=image.mode
    )

    result = pg_object.apply(image)

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
