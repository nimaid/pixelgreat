import os.path
import sys
import argparse
import warnings
import math
from PIL import Image

from .constants import ScreenType, Direction, DESCRIPTION, DEFAULTS, SUPPORTED_EXTENSIONS
from . import helpers
from . import filters


# ---- MAIN CLASSES AND FUNCTIONS ----

# The main reusable class that safely bridges user interaction with the filters
class Pixelgreat:
    def __init__(self,
                 output_size,
                 pixel_size,
                 screen_type=None,  # Set to a static default
                 direction=None,  # Set default based on screen type
                 pixel_aspect=None,  # Set to a static default
                 pixelate=None,  # Set to a static default
                 blur=None,  # Set default based on screen type
                 washout=None,  # Set default based on screen type
                 scanline_strength=None,  # Set default based on screen type
                 scanline_spacing=None,  # Set to a static default
                 scanline_size=None,  # Set to a static default
                 scanline_blur=None,  # Set to a static default
                 grid_strength=None,  # Set to a static default
                 pixel_padding=None,  # Set default based on screen type
                 rounding=None,  # Set default based on screen type
                 bloom_strength=None,  # Set to a static default
                 bloom_size=None,  # Set to a static default
                 color_mode=None  # Set to a static default
                 ):
        # Get basic settings used for all filters
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
            screen_type = DEFAULTS["screen_type"]
        if not isinstance(screen_type, ScreenType):
            raise ValueError("The screen_type argument must be a valid ScreenType instance")
        self.screen_type = screen_type

        if pixel_padding is None:
            # Set default based on screen type
            if self.screen_type == ScreenType.LCD:
                self.pixel_padding = DEFAULTS["pixel_padding"]["LCD"]
            elif self.screen_type == ScreenType.CRT_TV:
                self.pixel_padding = DEFAULTS["pixel_padding"]["CRT_TV"]
            else:  # Defaults to CRT monitor
                self.pixel_padding = DEFAULTS["pixel_padding"]["CRT_MONITOR"]
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
            if self.screen_type == ScreenType.LCD:
                self.direction = DEFAULTS["direction"]["LCD"]
            elif self.screen_type == ScreenType.CRT_TV:
                self.direction = DEFAULTS["direction"]["CRT_TV"]
            else:  # Defaults to CRT monitor
                self.direction = DEFAULTS["direction"]["CRT_MONITOR"]
        else:
            self.direction = direction

        if washout is None:
            # Set default based on screen type
            if self.screen_type == ScreenType.CRT_TV:
                self.washout = DEFAULTS["washout"]["CRT_TV"]
            elif self.screen_type == ScreenType.CRT_MONITOR:
                self.washout = DEFAULTS["washout"]["CRT_MONITOR"]
            else:  # Defaults to LCD
                self.washout = DEFAULTS["washout"]["LCD"]
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
                self.blur = DEFAULTS["blur"]["CRT_TV"]
            elif self.screen_type == ScreenType.CRT_MONITOR:
                self.blur = DEFAULTS["blur"]["CRT_MONITOR"]
            else:  # Defaults to LCD
                self.blur = DEFAULTS["blur"]["LCD"]
        else:
            helpers.assert_value_in_range(
                blur,
                minimum=0,
                maximum=1,
                message="Blur amount must be between {min} and {max} (got {val})"
            )
            self.blur = blur

        if bloom_size is None:
            bloom_size = DEFAULTS["bloom_size"]
        helpers.assert_value_in_range(
            bloom_size,
            minimum=0,
            maximum=1,
            message="Bloom size must be between {min} and {max} (got {val})"
        )
        self.bloom_size = bloom_size

        if pixel_aspect is None:
            pixel_aspect = DEFAULTS["pixel_aspect"]
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
                self.rounding = DEFAULTS["rounding"]["CRT_TV"]
            elif self.screen_type == ScreenType.CRT_MONITOR:
                self.rounding = DEFAULTS["rounding"]["CRT_MONITOR"]
            else:  # Defaults to LCD
                self.rounding = DEFAULTS["rounding"]["LCD"]
        else:
            helpers.assert_value_in_range(
                rounding,
                minimum=0,
                maximum=1,
                message="Rounding must be between {min} and {max} (got {val})"
            )
            self.rounding = rounding

        if scanline_spacing is None:
            scanline_spacing = DEFAULTS["scanline_spacing"]
        helpers.assert_value_in_range(
            scanline_spacing,
            minimum=0.33,
            maximum=3,
            message="Scanline spacing must be between {min} and {max} (got {val})"
        )
        self.scanline_spacing = scanline_spacing

        if scanline_size is None:
            scanline_size = DEFAULTS["scanline_size"]
        helpers.assert_value_in_range(
            scanline_size,
            minimum=0,
            maximum=1,
            message="Scanline size must be between {min} and {max} (got {val})"
        )
        self.scanline_size = scanline_size

        if scanline_blur is None:
            scanline_blur = DEFAULTS["scanline_blur"]
        helpers.assert_value_in_range(
            scanline_blur,
            minimum=0,
            maximum=1,
            message="Scanline blur must be between {min} and {max} (got {val})"
        )
        self.scanline_blur = scanline_blur

        if scanline_strength is None:
            # Set default based on screen type
            if self.screen_type == ScreenType.CRT_TV:
                self.scanline_strength = DEFAULTS["scanline_strength"]["CRT_TV"]
            elif self.screen_type == ScreenType.CRT_MONITOR:
                self.scanline_strength = DEFAULTS["scanline_strength"]["CRT_MONITOR"]
            else:  # Defaults to LCD
                self.scanline_strength = DEFAULTS["scanline_strength"]["LCD"]
        else:
            helpers.assert_value_in_range(
                scanline_strength,
                minimum=0,
                maximum=1,
                message="Scanline strength must be between {min} and {max} (got {val})"
            )
            self.scanline_strength = scanline_strength

        if bloom_strength is None:
            bloom_strength = DEFAULTS["bloom_strength"]
        helpers.assert_value_in_range(
            bloom_strength,
            minimum=0,
            maximum=1,
            message="Bloom strength must be between {min} and {max} (got {val})"
        )
        self.bloom_strength = bloom_strength

        if grid_strength is None:
            grid_strength = DEFAULTS["grid_strength"]
        helpers.assert_value_in_range(
            grid_strength,
            minimum=0,
            maximum=1,
            message="Grid strength must be between {min} and {max} (got {val})"
        )
        self.grid_strength = grid_strength

        if pixelate is None:
            pixelate = DEFAULTS["pixelate"]
        if not isinstance(pixelate, bool):
            raise ValueError("The pixelate argument must be a valid boolean value")
        self.pixelate = pixelate

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
        return self.filter.apply(image)

    def get_grid_filter(self, adjusted=False):
        return self.filter.get_grid_filter(adjusted=adjusted)

    def get_grid_filter_tile(self):
        return self.filter.get_grid_filter_tile()

    def get_scanline_filter(self, adjusted=False):
        return self.filter.get_scanline_filter(adjusted=adjusted)


# A single use helper function to process a single image
def pixelgreat(image,
               pixel_size,
               output_scale=1.0,
               screen_type=None,
               direction=None,
               pixel_aspect=None,
               pixelate=None,
               blur=None,
               washout=None,
               scanline_strength=None,
               scanline_spacing=None,
               scanline_size=None,
               scanline_blur=None,
               grid_strength=None,
               pixel_padding=None,
               rounding=None,
               bloom_strength=None,
               bloom_size=None
               ):
    output_size = (
        max(round(image.width * output_scale), 3),
        max(round(image.height * output_scale), 3)
    )
    pg_object = Pixelgreat(
        output_size=output_size,
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
        color_mode=image.mode
    )
    result = pg_object.apply(image)

    return result


# ---- PROGRAM EXECUTION ----


# Parse arguments for a single image
def parse_args_single(args):
    parser = argparse.ArgumentParser(
        description=f"{DESCRIPTION}\n\n"
                    f"Valid values are shown in {{braces}}\n"
                    f"Default values are shown in [brackets]",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("-i", "--input", dest="image_in", type=helpers.file_path, required=True,
                        help="the image to convert"
                        )

    parser.add_argument("-o", "--output", dest="image_out", type=str, required=True,
                        help="where to save the converted image, and what filetype to save it as"
                        )

    parser.add_argument("-s", "--size", dest="pixel_size", type=float, required=True,
                        help="the size of the pixels {3 - no limit}"
                        )

    parser.add_argument("-os", "--output-scale", dest="output_scale", type=float, required=False,
                        default=None,
                        help="How much to scale the output size by {no limits, 1.0 is no scaling, 2.0 is 2x size} [1.0]"
                        )

    parser.add_argument("-t", "--type", dest="screen_type", type=str, required=False,
                        default=None,
                        help="the type of RGB filter to apply {{{lcd}, {crt_tv}, {crt_mon}}} [{default}]".format(
                            lcd=ScreenType.LCD.value,
                            crt_tv=ScreenType.CRT_TV.value,
                            crt_mon=ScreenType.CRT_MONITOR.value,
                            default=DEFAULTS["screen_type"].value)
                        )

    parser.add_argument("-d", "--direction", dest="direction", type=str, required=False,
                        default=None,
                        help="the direction of the RGB filter {{{vert}, {horiz}}} [varies w/ screen type]".format(
                            vert=Direction.VERTICAL.value,
                            horiz=Direction.HORIZONTAL.value)
                        )

    parser.add_argument("-a", "--aspect", dest="pixel_aspect", type=float, required=False,
                        default=None,
                        help="the aspect ratio of the pixels, width / height {{0.33 - 3.0}} [{default}]".format(
                            default=DEFAULTS["pixel_aspect"])
                        )

    parser.add_argument("-npx", "--no-pixelate", dest="pixelate", action="store_false",
                        help="if given, the image will not be pixelated, but the other filters will still be applied"
                        )

    parser.add_argument("-b", "--blur", dest="blur_amount", type=float, required=False,
                        default=None,
                        help="how much to blur the source image {0.0 - 1.0} [varies w/ screen type]"
                        )

    parser.add_argument("-w", "--washout", dest="washout", type=float, required=False,
                        default=None,
                        help="how much to brighten dark pixels {0.0 - 1.0} [varies w/ screen type]"
                        )

    parser.add_argument("-sst", "--scanline-strength", dest="scanline_strength", type=float, required=False,
                        default=None,
                        help="the strength of the CRT scanline filter {0.0 - 1.0} [varies w/ screen type]"
                        )

    parser.add_argument("-ssp", "--scanline-spacing", dest="scanline_spacing", type=float, required=False,
                        default=None,
                        help="how far apart to space the CRT scanlines {{0.33 - 3.0}} [{default}]".format(
                            default=DEFAULTS["scanline_spacing"])
                        )

    parser.add_argument("-ssz", "--scanline-size", dest="scanline_size", type=float, required=False,
                        default=None,
                        help="how wide the CRT scanlines are {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["scanline_size"])
                        )

    parser.add_argument("-sb", "--scanline-blur", dest="scanline_blur", type=float, required=False,
                        default=None,
                        help="how much blur to apply to the CRT scanline filter {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["scanline_blur"])
                        )

    parser.add_argument("-gst", "--grid-strength", dest="grid_strength", type=float, required=False,
                        default=None,
                        help="the strength of the RGB pixel grid filter {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["grid_strength"])
                        )

    parser.add_argument("-p", "--padding", dest="padding", type=float, required=False,
                        default=None,
                        help="how much black padding to add around the pixels {0.0 - 1.0} [varies w/ screen type]"
                        )

    parser.add_argument("-r", "--rounding", dest="rounding", type=float, required=False,
                        default=None,
                        help="how much to round the corners of the pixels {0.0 - 1.0} [varies w/ screen type]"
                        )

    parser.add_argument("-bst", "--bloom-strength", dest="bloom_strength", type=float, required=False,
                        default=None,
                        help="the amount of bloom to add to the output image {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["bloom_strength"])
                        )

    parser.add_argument("-bsz", "--bloom-size", dest="bloom_size", type=float, required=False,
                        default=None,
                        help="the size of the bloom added to the output image {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["bloom_size"])
                        )

    parsed_args = parser.parse_args()

    # Interpret string arguments
    if parsed_args.screen_type is not None:
        if parsed_args.screen_type == ScreenType.LCD.value:
            parsed_args.screen_type = ScreenType.LCD
        elif parsed_args.screen_type == ScreenType.CRT_TV.value:
            parsed_args.screen_type = ScreenType.CRT_TV
        elif parsed_args.screen_type == ScreenType.CRT_MONITOR.value:
            parsed_args.screen_type = ScreenType.CRT_MONITOR
        else:
            parser.error(f"\"{parsed_args.screen_type}\" is not a valid screen type")

    if parsed_args.direction is not None:
        if parsed_args.direction == Direction.VERTICAL.value:
            parsed_args.direction = Direction.VERTICAL
        elif parsed_args.direction == Direction.HORIZONTAL.value:
            parsed_args.direction = Direction.HORIZONTAL
        else:
            parser.error(f"\"{parsed_args.direction}\" is not a valid direction")

    # Verify the target file extensions are supported
    input_name, input_ext = os.path.splitext(parsed_args.image_in)
    input_ext = input_ext.lower()
    if input_ext not in SUPPORTED_EXTENSIONS:
        parser.error(f"\"{input_ext}\" is not a supported input format")

    output_name, output_ext = os.path.splitext(parsed_args.image_out)
    output_ext = output_ext.lower()
    if output_ext not in SUPPORTED_EXTENSIONS:
        parser.error(f"\"{output_ext}\" is not a supported output format")

    return parsed_args


# Process a single image
def single(raw_args):
    # Parse args
    args = parse_args_single(raw_args)

    # Open source image
    image = Image.open(args.image_in)

    # Apply the filter to a single image
    result = pixelgreat(image=image,
                        pixel_size=args.pixel_size,
                        screen_type=args.screen_type,
                        pixel_padding=args.padding,
                        direction=args.direction,
                        washout=args.washout,
                        blur=args.blur_amount,
                        bloom_size=args.bloom_size,
                        pixel_aspect=args.pixel_aspect,
                        rounding=args.rounding,
                        scanline_spacing=args.scanline_spacing,
                        scanline_size=args.scanline_size,
                        scanline_blur=args.scanline_blur,
                        scanline_strength=args.scanline_strength,
                        bloom_strength=args.bloom_strength,
                        grid_strength=args.grid_strength,
                        pixelate=args.pixelate,
                        output_scale=args.output_scale
                        )
    # TODO:
    result.show()


# Wrapper for processing a single image
def run_single():
    single(sys.argv[1:])


# Parse arguments for an image sequence
def parse_args_sequence(args):
    parser = argparse.ArgumentParser(
        description=f"{DESCRIPTION}\n\n"
                    f"Valid values are shown in {{braces}}\n"
                    f"Default values are shown in [brackets]\n\n"
                    f"For image sequences, the output size is based on the first image in the sequence",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    '''
    parser.add_argument("-i", "--input", dest="image_in", type=helpers.file_path, required=True,
                        help="the image to convert"
                        )
    '''
    '''
    parser.add_argument("-o", "--output", dest="image_out", type=str, required=True,
                        help="where to save the converted image, and what filetype to save it as"
                        )
    '''
    parser.add_argument("-s", "--size", dest="pixel_size", type=float, required=True,
                        help="the size of the pixels {3 - no limit}"
                        )

    parser.add_argument("-os", "--output-scale", dest="output_scale", type=float, required=False,
                        default=None,
                        help="How much to scale the output size by {no limits, 1.0 is no scaling, 2.0 is 2x size} [1.0]"
                        )

    parser.add_argument("-t", "--type", dest="screen_type", type=str, required=False,
                        default=None,
                        help="the type of RGB filter to apply {{{lcd}, {crt_tv}, {crt_mon}}} [{default}]".format(
                            lcd=ScreenType.LCD.value,
                            crt_tv=ScreenType.CRT_TV.value,
                            crt_mon=ScreenType.CRT_MONITOR.value,
                            default=DEFAULTS["screen_type"].value)
                        )

    parser.add_argument("-d", "--direction", dest="direction", type=str, required=False,
                        default=None,
                        help="the direction of the RGB filter {{{vert}, {horiz}}} [varies w/ screen type]".format(
                            vert=Direction.VERTICAL.value,
                            horiz=Direction.HORIZONTAL.value)
                        )

    parser.add_argument("-a", "--aspect", dest="pixel_aspect", type=float, required=False,
                        default=None,
                        help="the aspect ratio of the pixels, width / height {{0.33 - 3.0}} [{default}]".format(
                            default=DEFAULTS["pixel_aspect"])
                        )

    parser.add_argument("-npx", "--no-pixelate", dest="pixelate", action="store_false",
                        help="if given, the image will not be pixelated, but the other filters will still be applied"
                        )

    parser.add_argument("-b", "--blur", dest="blur_amount", type=float, required=False,
                        default=None,
                        help="how much to blur the source image {0.0 - 1.0} [varies w/ screen type]"
                        )

    parser.add_argument("-w", "--washout", dest="washout", type=float, required=False,
                        default=None,
                        help="how much to brighten dark pixels {0.0 - 1.0} [varies w/ screen type]"
                        )

    parser.add_argument("-sst", "--scanline-strength", dest="scanline_strength", type=float, required=False,
                        default=None,
                        help="the strength of the CRT scanline filter {0.0 - 1.0} [varies w/ screen type]"
                        )

    parser.add_argument("-ssp", "--scanline-spacing", dest="scanline_spacing", type=float, required=False,
                        default=None,
                        help="how far apart to space the CRT scanlines {{0.33 - 3.0}} [{default}]".format(
                            default=DEFAULTS["scanline_spacing"])
                        )

    parser.add_argument("-ssz", "--scanline-size", dest="scanline_size", type=float, required=False,
                        default=None,
                        help="how wide the CRT scanlines are {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["scanline_size"])
                        )

    parser.add_argument("-sb", "--scanline-blur", dest="scanline_blur", type=float, required=False,
                        default=None,
                        help="how much blur to apply to the CRT scanline filter {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["scanline_blur"])
                        )

    parser.add_argument("-gst", "--grid-strength", dest="grid_strength", type=float, required=False,
                        default=None,
                        help="the strength of the RGB pixel grid filter {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["grid_strength"])
                        )

    parser.add_argument("-p", "--padding", dest="padding", type=float, required=False,
                        default=None,
                        help="how much black padding to add around the pixels {0.0 - 1.0} [varies w/ screen type]"
                        )

    parser.add_argument("-r", "--rounding", dest="rounding", type=float, required=False,
                        default=None,
                        help="how much to round the corners of the pixels {0.0 - 1.0} [varies w/ screen type]"
                        )

    parser.add_argument("-bst", "--bloom-strength", dest="bloom_strength", type=float, required=False,
                        default=None,
                        help="the amount of bloom to add to the output image {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["bloom_strength"])
                        )

    parser.add_argument("-bsz", "--bloom-size", dest="bloom_size", type=float, required=False,
                        default=None,
                        help="the size of the bloom added to the output image {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["bloom_size"])
                        )

    parsed_args = parser.parse_args()

    # Interpret string arguments
    if parsed_args.screen_type is not None:
        if parsed_args.screen_type == ScreenType.LCD.value:
            parsed_args.screen_type = ScreenType.LCD
        elif parsed_args.screen_type == ScreenType.CRT_TV.value:
            parsed_args.screen_type = ScreenType.CRT_TV
        elif parsed_args.screen_type == ScreenType.CRT_MONITOR.value:
            parsed_args.screen_type = ScreenType.CRT_MONITOR
        else:
            parser.error(f"\"{parsed_args.screen_type}\" is not a valid screen type")

    if parsed_args.direction is not None:
        if parsed_args.direction == Direction.VERTICAL.value:
            parsed_args.direction = Direction.VERTICAL
        elif parsed_args.direction == Direction.HORIZONTAL.value:
            parsed_args.direction = Direction.HORIZONTAL
        else:
            parser.error(f"\"{parsed_args.direction}\" is not a valid direction")

    # Verify the target file extensions are supported
    '''
    input_name, input_ext = os.path.splitext(parsed_args.image_in)
    input_ext = input_ext.lower()
    if input_ext not in SUPPORTED_EXTENSIONS:
        parser.error(f"\"{input_ext}\" is not a supported input format")

    output_name, output_ext = os.path.splitext(parsed_args.image_out)
    output_ext = output_ext.lower()
    if output_ext not in SUPPORTED_EXTENSIONS:
        parser.error(f"\"{output_ext}\" is not a supported output format")
    '''

    return parsed_args


# Process an image sequence
def sequence(raw_args):
    # args = parse_args_sequence(raw_args)
    print("Image sequences are not yet implemented. Soon.™")


# Wrapper for processing an image sequence
def run_sequence():
    sequence(sys.argv[1:])
