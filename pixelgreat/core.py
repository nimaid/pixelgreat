import os
import argparse
import warnings
import time
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
                 brighten=None,  # Set to a static default
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

        if brighten is None:
            self.brighten = DEFAULTS["brighten"]
        else:
            helpers.assert_value_in_range(
                brighten,
                minimum=0,
                maximum=1,
                message="Brighten amount must be between {min} and {max} (got {val})"
            )
            self.brighten = brighten

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
            brighten=self.brighten,
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
               output_scale=None,
               screen_type=None,
               direction=None,
               pixel_aspect=None,
               pixelate=None,
               brighten=None,
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
    if output_scale is None:
        output_scale = DEFAULTS["output_scale"]

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
        brighten=brighten,
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
def parse_args_single():
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

    parser.add_argument("-br", "--brighten", dest="brighten", type=float, required=False,
                        default=None,
                        help="how much to brighten the source image {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["brighten"])
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
def single():
    # Parse args
    args = parse_args_single()

    # Open source image
    image = Image.open(os.path.realpath(args.image_in))

    start_time = time.time()

    # Apply the filter to a single image
    print("Converting image...")
    result = pixelgreat(image=image,
                        pixel_size=args.pixel_size,
                        screen_type=args.screen_type,
                        pixel_padding=args.padding,
                        direction=args.direction,
                        washout=args.washout,
                        brighten=args.brighten,
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

    # Save it
    print("Saving image...")
    output_name = os.path.realpath(args.image_out)
    output_dir = os.path.dirname(output_name)
    os.makedirs(output_dir, exist_ok=True)
    result.save(output_name)

    end_time = time.time()
    process_time = round(end_time - start_time, 1)

    print(f"Done converting 1 image in {process_time} seconds!\nSaved image: {args.image_out}")


# Parse arguments for an image sequence
def parse_args_sequence():
    parser = argparse.ArgumentParser(
        description=f"{DESCRIPTION}\n\n"
                    f"Valid values are shown in {{braces}}\n"
                    f"Default values are shown in [brackets]\n\n"
                    f"For image sequences, the output size is based on the first image in the sequence",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("-i", "--input", dest="image_in", type=helpers.file_path, required=True,
                        help="the image to convert (must be part of a sequence)"
                        )

    parser.add_argument("-o", "--output", dest="image_out", type=str, required=True,
                        help="where to save the converted image sequence, and what filetype to save them as"
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

    parser.add_argument("-br", "--brighten", dest="brighten", type=float, required=False,
                        default=None,
                        help="how much to brighten the source image {{0.0 - 1.0}} [{default}]".format(
                            default=DEFAULTS["brighten"])
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

    # Validate the input image actually represents an image sequence
    if helpers.parse_sequenced_image_name(parsed_args.image_in)["error"] is not None:
        parser.error("No image sequence found. Ensure they are named like this: name0000.png, name0001.png, etc.")

    # Set default scale
    if parsed_args.output_scale is None:
        parsed_args.output_scale = 1.0

    return parsed_args


# Process an image sequence
def sequence():
    args = parse_args_sequence()
    print("Preparing to process image sequence...")

    start_time = time.time()

    # Get the full image sequence
    sequence_info = helpers.get_all_images_in_sequence(args.image_in)

    # Get the size and color mode of the first image
    first_image = Image.open(sequence_info["files"][0])
    first_image_size = first_image.size
    first_image_mode = first_image.mode
    first_image.close()

    # Get the output size
    output_size = (
        max(round(first_image_size[0] * args.output_scale), 3),
        max(round(first_image_size[1] * args.output_scale), 3)
    )

    # Make the re-usable converter object
    converter = Pixelgreat(
        output_size=output_size,
        pixel_size=args.pixel_size,
        screen_type=args.screen_type,
        pixel_padding=args.padding,
        direction=args.direction,
        washout=args.washout,
        brighten=args.brighten,
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
        color_mode=first_image_mode
    )

    # Make the destination dir if it doesn't already exist
    output_dir = os.path.dirname(args.image_out)
    os.makedirs(output_dir, exist_ok=True)

    # Loop through the images
    image_count = len(sequence_info["files"])
    for i, image_name in enumerate(sequence_info["files"]):
        print(f"Converting image {i + 1} of {image_count}...")

        # Open image
        image_in = Image.open(image_name)

        # Convert the image with the reusable converter
        image_out = converter.apply(image_in)

        # Get new image filename
        main_name, ext = os.path.splitext(args.image_out)
        this_number = str(i).rjust(sequence_info["digits"], "0")
        output_name = f"{main_name}{this_number}{ext}"

        print(f"  Saving image...")

        # Save the image
        try:
            image_out.save(output_name)
        except OSError as e:
            # Try converting it to RGB first
            rgb_image_out = image_out.convert("RGB")
            rgb_image_out.save(output_name)
            rgb_image_out.close()

        # Close the images
        image_in.close()
        image_out.close()

    end_time = time.time()
    process_time = round(end_time - start_time, 1)

    print(f"Done converting {image_count} images in {process_time} seconds!\n"
          f"Saved images to {output_dir}")
