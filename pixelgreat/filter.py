import math
from PIL import Image, ImageDraw, ImageChops, ImageFilter

import helpers
from constants import Direction, ScreenType


def lcd(size, padding, direction, aspect, rounding, color_mode="RGB"):
    # Adjust aspect for later rotation if needed
    if direction == Direction.VERTICAL:
        aspect = 1 / aspect

    # Get main pixel dimensions (float, used in calculations)
    width = size
    height = size / aspect

    # Get integer values for width and height (the REAL pixel count)
    width_px = round(width)
    height_px = round(height)

    # Make new black image
    filter_image = Image.new(color_mode, (width_px, height_px), (0, 0, 0))

    # Make drawing object
    filter_draw = ImageDraw.Draw(filter_image)

    # Get padding pixels based on size (1.0 should just barely block out all RGB, 0.0 should equal 0 px)
    if aspect < 3.0:
        padding_px = round(padding * (width / 3))
    else:
        padding_px = round(padding * height)

    # If padding is 0, make sure it's actually 0 so that we can draw full color bars later
    if padding <= 0.0:
        padding_px = 0

    # If it's 1.0, we know it should be full black, so we should return the black image now
    if padding >= 1.0:
        return filter_image

    # Get left and right padding amounts
    padding_left = math.ceil(padding_px / 2)  # Also used for tops
    padding_right = padding_px - padding_left  # Also used for bottoms

    # Get variables use for drawing the color regions
    rg_boundary_x = round(width / 3)
    gb_boundary_x = round((2 * width) / 3)

    if padding_px == 0:
        red_start = (0, 0)
        red_end = (rg_boundary_x - 1, height_px - 1)

        green_start = (rg_boundary_x, 0)
        green_end = (gb_boundary_x - 1, height_px - 1)

        blue_start = (gb_boundary_x, 0)
        blue_end = (width_px - 1, height_px - 1)
    else:
        red_start = (padding_left, padding_left)
        red_end = (
            max((rg_boundary_x - padding_right) - 1, red_start[0]),
            max((height_px - padding_right) - 1, red_start[1])
        )

        green_start = (rg_boundary_x + padding_left, padding_left)
        green_end = (
            max((gb_boundary_x - padding_right) - 1, green_start[0]),
            max((height_px - padding_right) - 1, green_start[1])
        )

        blue_start = (gb_boundary_x + padding_left, padding_left)
        blue_end = (
            max((width_px - padding_right) - 1, blue_start[0]),
            max((height_px - padding_right) - 1, blue_start[1])
        )

    color_size_px = red_end[0] - red_start[0]

    # Draw color regions
    if rounding > 0:
        round_radius = round((color_size_px / 2) * rounding)

        filter_draw.rounded_rectangle((red_start, red_end), fill=(255, 0, 0), radius=round_radius)
        filter_draw.rounded_rectangle((green_start, green_end), fill=(0, 255, 0), radius=round_radius)
        filter_draw.rounded_rectangle((blue_start, blue_end), fill=(0, 0, 255), radius=round_radius)
    else:
        filter_draw.rectangle((red_start, red_end), fill=(255, 0, 0))
        filter_draw.rectangle((green_start, green_end), fill=(0, 255, 0))
        filter_draw.rectangle((blue_start, blue_end), fill=(0, 0, 255))

    # Rotate if needed
    if direction == Direction.HORIZONTAL:
        filter_image = filter_image.rotate(270, expand=True)

    return filter_image


def crt_tv(size, padding, direction, aspect, rounding, color_mode="RGB"):
    # Adjust aspect for later rotation if needed
    if direction == Direction.VERTICAL:
        aspect = 1 / aspect

    # Get the first half of the filter
    single_pixel = lcd(size=size,
                       padding=padding,
                       direction=Direction.VERTICAL,
                       aspect=aspect,
                       rounding=rounding,
                       color_mode=color_mode
                       )

    # Figure out the dimensions for the new filter
    new_size = (single_pixel.width * 2, single_pixel.height)

    # Make new image to paste old one onto
    both_pixels = Image.new(color_mode, new_size, color=(0, 0, 0))

    # Paste the first pixel
    both_pixels.paste(single_pixel, (0, 0))

    # Paste the second pixel in two parts
    split_y = round(both_pixels.height / 2)
    both_pixels.paste(single_pixel, (single_pixel.width, split_y))
    both_pixels.paste(single_pixel, (single_pixel.width, split_y - single_pixel.height))

    # Rotate if needed
    if direction == Direction.HORIZONTAL:
        both_pixels = both_pixels.rotate(270, expand=True)

    return both_pixels


def crt_monitor(size, padding, direction, color_mode="RGB"):
    # Adjust size to more correctly match real mapping for pixel sizes
    size = (size / math.sqrt(3))

    # Get width and height from dot size (float, used for calculations)
    width = size * 3
    height = size * math.sqrt(3)

    # Get integer divisions for dot placement
    height_divs = (
        0,
        round(height / 2),
        round(height)
    )
    width_divs = (
        0,
        round(width * (1 / 6)),
        round(width * (2 / 6)),
        round(width * (3 / 6)),
        round(width * (4 / 6)),
        round(width * (5 / 6)),
        round(width)
    )

    # Make new black image
    filter_image = Image.new(color_mode, (width_divs[-1], height_divs[-1]), (0, 0, 0))

    # Make drawing object
    filter_draw = ImageDraw.Draw(filter_image)

    # If padding is  1, know it should be full black, so we should return the black image now
    if padding == 1:
        return filter_image

    # Get dot size
    dot_size = size * (1 - padding)

    # Draw red dots
    filter_draw.ellipse(
        helpers.get_centered_dimensions((width_divs[0], height_divs[0]), (dot_size, dot_size)),
        fill=(255, 0, 0)
    )
    filter_draw.ellipse(
        helpers.get_centered_dimensions((width_divs[6], height_divs[0]), (dot_size, dot_size)),
        fill=(255, 0, 0)
    )
    filter_draw.ellipse(
        helpers.get_centered_dimensions((0, height_divs[2]), (dot_size, dot_size)),
        fill=(255, 0, 0)
    )
    filter_draw.ellipse(
        helpers.get_centered_dimensions((width_divs[6], height_divs[2]), (dot_size, dot_size)),
        fill=(255, 0, 0)
    )
    filter_draw.ellipse(
        helpers.get_centered_dimensions((width_divs[3], height_divs[1]), (dot_size, dot_size)),
        fill=(255, 0, 0)
    )

    # Draw green dots
    filter_draw.ellipse(
        helpers.get_centered_dimensions((width_divs[2], height_divs[0]), (dot_size, dot_size)),
        fill=(0, 255, 0)
    )
    filter_draw.ellipse(
        helpers.get_centered_dimensions((width_divs[2], height_divs[2]), (dot_size, dot_size)),
        fill=(0, 255, 0)
    )
    filter_draw.ellipse(
        helpers.get_centered_dimensions((width_divs[5], height_divs[1]), (dot_size, dot_size)),
        fill=(0, 255, 0)
    )

    # Draw blue dots
    filter_draw.ellipse(
        helpers.get_centered_dimensions((width_divs[1], height_divs[1]), (dot_size, dot_size)),
        fill=(0, 0, 255)
    )
    filter_draw.ellipse(
        helpers.get_centered_dimensions((width_divs[4], height_divs[0]), (dot_size, dot_size)),
        fill=(0, 0, 255)
    )
    filter_draw.ellipse(
        helpers.get_centered_dimensions((width_divs[4], height_divs[2]), (dot_size, dot_size)),
        fill=(0, 0, 255)
    )

    # Rotate if needed
    if direction == Direction.VERTICAL:
        filter_image = filter_image.rotate(270, expand=True)

    return filter_image


def scanlines(size, spacing, line_size, blur, direction, color_mode="RGB"):
    # Create new black image for building the scanline filter
    scanline_image = Image.new(color_mode, size, color=(0, 0, 0))

    # If the line size is 0, we know it should be all black
    if line_size == 0:
        return scanline_image

    # Make drawing object
    scanline_draw = ImageDraw.Draw(scanline_image)

    # Get line width (integer)
    line_width = round(spacing * line_size)

    # Draw hard lines
    if direction == Direction.HORIZONTAL:
        line_count = math.ceil(scanline_image.height / spacing)
        for line in range(line_count):
            line_start_y = round(line * spacing)
            line_end_y = line_start_y + line_width

            scanline_draw.rectangle(((0, line_start_y), (scanline_image.width, line_end_y)), fill=(255, 255, 255))
    else:
        line_count = math.ceil(scanline_image.width / spacing)
        for line in range(line_count):
            line_start_x = round(line * spacing)
            line_end_x = line_start_x + line_width

            scanline_draw.rectangle(((line_start_x, 0), (line_end_x, scanline_image.height)), fill=(255, 255, 255))

    # Apply blur
    if blur > 0:
        blur_amt = line_width * blur
        scanline_image = scanline_image.filter(ImageFilter.GaussianBlur(blur_amt))

    return scanline_image


def pixelate_image(image,
                   pixel_size,
                   pixel_aspect,
                   direction,
                   output_size=None,  # Defaults to the input image size
                   downscale_mode=Image.Resampling.HAMMING
                   ):
    if output_size is None:
        output_size = image.size

    # Adjust aspect to horizontal if not horizontal (matches pattern in lcd)
    if direction == Direction.VERTICAL:
        pixel_aspect = 1 / pixel_aspect

    # Calculate pixel height
    pixel_height = pixel_size * pixel_aspect

    # Calculate approximate pixel counts to match target size
    pixels_wide = round(output_size[0] / pixel_size)
    pixels_tall = round(output_size[1] / pixel_height)

    # Downscale image
    small_image = image.resize((pixels_wide, pixels_tall), resample=downscale_mode)

    # Upscale to the final size
    result = small_image.resize(output_size, resample=Image.Resampling.NEAREST)

    return result


# A reusable class to handle applying scanlines
class ScanlineFilter:
    def __init__(self,
                 size,
                 line_spacing,
                 line_size,
                 line_blur,
                 direction,
                 strength=1.0,
                 color_mode="RGB"
                 ):
        self.size = size

        self.line_spacing = line_spacing

        self.line_size = line_size

        self.line_blur = line_blur

        self.direction = direction

        self.strength = strength

        self.color_mode = color_mode

        # Pre-compute filter image
        self.filter_raw = scanlines(
            size=self.size,
            spacing=self.line_spacing,
            line_size=self.line_size,
            blur=self.line_blur,
            direction=self.direction,
            color_mode=self.color_mode
        )

        # Pre-computed adjusted filter image
        self.filter = helpers.lighten_image(self.filter_raw, 1 - self.strength)

    # Apply the filter to a desired image
    def apply(self, image):
        if image.size != self.size:
            raise ValueError(f"Input image size \"{image.size}\" "
                             f"does not match filter size \"{self.size}\"")
        if image.mode != self.color_mode:
            raise ValueError(f"Input image color mode \"{image.mode}\" "
                             f"does not match filter color mode \"{self.color_mode}\"")

        result = ImageChops.multiply(image, self.filter)

        return result


# A reusable class to handle applying the RGB filter
class ScreenFilter:
    def __init__(self,
                 size,
                 screen_type,
                 pixel_size,
                 pixel_padding,
                 direction,
                 pixel_aspect=None,
                 rounding=None,
                 strength=1.0,
                 color_mode="RGB"
                 ):
        self.size = size

        self.screen_type = screen_type

        self.pixel_size = pixel_size

        self.pixel_padding = pixel_padding

        self.direction = direction

        self.pixel_aspect = pixel_aspect
        self.rounding = rounding

        self.color_mode = color_mode

        # Get the filter tile image
        if self.screen_type == ScreenType.CRT_MONITOR:
            self.filter_tile = crt_monitor(
                size=self.pixel_size,
                padding=self.pixel_padding,
                direction=self.direction,
                color_mode=self.color_mode
            )
        elif self.screen_type == ScreenType.CRT_TV:
            self.filter_tile = crt_tv(
                size=self.pixel_size,
                padding=self.pixel_padding,
                direction=self.direction,
                aspect=self.pixel_aspect,
                rounding=self.rounding,
                color_mode=self.color_mode
            )
        else:  # Default to LCD
            self.filter_tile = lcd(
                size=self.pixel_size,
                padding=self.pixel_padding,
                direction=self.direction,
                aspect=self.pixel_aspect,
                rounding=self.rounding,
                color_mode=self.color_mode
            )

        self.strength = strength

        # Pre-compute a tiled filter image
        self.filter_raw = helpers.tile_image(self.filter_tile, self.size)

        # Pre-computed adjusted filter image
        self.filter = helpers.lighten_image(self.filter_raw, 1 - self.strength)

    # Apply the filter to a desired image
    def apply(self, image):
        if image.size != self.size:
            raise ValueError(f"Input image size \"{image.size}\" "
                             f"does not match filter size \"{self.size}\"")
        if image.mode != self.color_mode:
            raise ValueError(f"Input image color mode \"{image.mode}\" "
                             f"does not match filter color mode \"{self.color_mode}\"")

        result = ImageChops.multiply(image, self.filter)

        return result


# A reusable class to handle the composite effects
class CompositeFilter:
    def __init__(self,
                 size,
                 screen_type,
                 pixel_size,
                 pixel_padding,
                 direction,
                 blur=0.0,
                 pixel_aspect=None,
                 rounding=None,
                 scanline_spacing=None,
                 scanline_size=None,
                 scanline_blur=None,
                 scanline_strength=None,  # Default set based on screen_type
                 grid_strength=1.0,
                 pixelate=True,
                 output_size=None,  # Defaults to size
                 color_mode="RGB"
                 ):
        self.size = size

        self.screen_type = screen_type

        self.pixel_size = pixel_size

        self.pixel_padding = pixel_padding

        self.direction = direction

        self.blur = blur
        self.blur_px = round((self.pixel_size  / 2) * blur)

        self.pixel_aspect = pixel_aspect

        self.rounding = rounding

        self.scanline_spacing = scanline_spacing

        self.scanline_size = scanline_size

        self.scanline_blur = scanline_blur

        self.scanline_strength = scanline_strength

        self.grid_strength = grid_strength

        self.pixelate = pixelate

        if output_size is None:
            self.output_size = self.size
        else:
            self.output_size = output_size

        self.color_mode = color_mode

        # Set default scanline_strength based on screen type
        if self.scanline_strength is None:
            if self.screen_type in [ScreenType.CRT_TV, ScreenType.CRT_MONITOR]:
                self.scanline_strength = 1.0
            else:
                self.scanline_strength = 0.0

        # Get scanline direction based on screen type
        if self.screen_type in [ScreenType.CRT_MONITOR]:
            self.scanline_direction = self.direction
        else:
            if self.direction == Direction.HORIZONTAL:
                self.scanline_direction = Direction.VERTICAL
            else:
                self.scanline_direction = Direction.HORIZONTAL

        # Make sure we have required variables for each situation
        if self.grid_strength > 0:
            if self.screen_type in [ScreenType.LCD, ScreenType.CRT_TV]:
                if self.pixel_aspect is None:
                    raise ValueError("This screen type requires the argument pixel_aspect")
                if self.rounding is None:
                    raise ValueError("This screen type requires the argument rounding")

        if self.scanline_strength > 0:
            if self.scanline_spacing is None:
                raise ValueError("Scanlines are enabled, requires the argument scanline_spacing")
            if self.scanline_size is None:
                raise ValueError("Scanlines are enabled, requires the argument scanline_size")
            if self.scanline_blur is None:
                raise ValueError("Scanlines are enabled, requires the argument scanline_blur")

        if self.pixelate:
            if self.pixel_aspect is None:
                raise ValueError("Pixelate enabled, requires the argument pixel_aspect")

        # Make the scanline filter object (if needed)
        if self.scanline_strength > 0:
            self.scanline_filter = ScanlineFilter(
                size=self.output_size,
                line_spacing=self.scanline_spacing,
                line_size=self.scanline_size,
                line_blur=self.scanline_blur,
                direction=self.scanline_direction,
                strength=self.scanline_strength,
                color_mode=self.color_mode
            )
        else:
            self.scanline_filter = None

        # Make the screen filter object (if needed)
        if self.grid_strength > 0:
            self.screen_filter = ScreenFilter(
                size=self.output_size,
                screen_type=self.screen_type,
                pixel_size=self.pixel_size,
                pixel_padding=self.pixel_padding,
                direction=self.direction,
                pixel_aspect=self.pixel_aspect,
                rounding=self.rounding,
                strength=self.grid_strength,
                color_mode=self.color_mode
            )
        else:
            self.screen_filter = None

    # Apply the filter to a desired image
    def apply(self, image):
        if image.size != self.size:
            raise ValueError(f"Input image size \"{image.size}\" "
                             f"does not match filter size \"{self.size}\"")
        if image.mode != self.color_mode:
            raise ValueError(f"Input image color mode \"{image.mode}\" "
                             f"does not match filter color mode \"{self.color_mode}\"")

        # Pixelate / scale to final size
        if self.pixelate:
            result = pixelate_image(
                image=image,
                pixel_size=self.pixel_size,
                pixel_aspect=self.pixel_aspect,
                direction=self.direction,
                output_size=self.output_size
            )
        else:
            if image.size != self.output_size:
                result = image.resize(self.output_size, resample=Image.Resampling.NEAREST)
            else:
                result = image.copy()

        # Blur, if relevant
        if self.blur > 0:
            result = result.filter(ImageFilter.GaussianBlur(self.blur_px))

        # Add scanlines if applicable
        if self.scanline_filter is not None:
            result = self.scanline_filter.apply(result)

        # Add pixel grid if applicable
        if self.screen_filter is not None:
            result = self.screen_filter.apply(result)

        return result
