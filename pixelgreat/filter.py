import math
from PIL import Image, ImageDraw, ImageChops

import helpers
from constants import Direction, ScreenType


def lcd(size, padding, direction, aspect, rounding):
    # Clip size (minimum of 3)
    size = max(size, 3)

    # Get main pixel dimensions (float, used in calculations)
    width = size
    height = size / aspect

    # Get integer values for width and height (the REAL pixel count)
    width_px = round(width)
    height_px = round(height)

    # Make new black image
    filter_image = Image.new("RGB", (width_px, height_px), (0, 0, 0))

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


def crt_tv(size, padding, direction, aspect, rounding):
    # Get the first half of the filter
    single_pixel = lcd(size=size,
                       padding=padding,
                       direction=Direction.VERTICAL,
                       aspect=aspect,
                       rounding=rounding
                       )

    # Figure out the dimensions for the new filter
    new_size = (single_pixel.width * 2, single_pixel.height)

    # Make new image to paste old one onto
    both_pixels = Image.new("RGB", new_size, color=(0, 0, 0))

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


def crt_monitor(size, padding, direction):
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
    filter_image = Image.new("RGB", (width_divs[-1], height_divs[-1]), (0, 0, 0))

    # Make drawing object
    filter_draw = ImageDraw.Draw(filter_image)

    # Clip padding
    padding = helpers.clip(padding, 0, 1)

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


class ScreenFilter:
    def __init__(self,
                 size,
                 screen_type,
                 pixel_size,
                 pixel_padding,
                 direction,
                 pixel_aspect=None,
                 rounding=None,
                 strength=1.0
                 ):
        self.size = size

        self.screen_type = screen_type

        self.pixel_size = pixel_size

        self.pixel_padding = pixel_padding

        self.direction = direction

        if self.screen_type in [ScreenType.LCD, ScreenType.CRT_TV]:
            if pixel_aspect is None:
                raise ValueError("This screen type requires the argument pixel_aspect")
            if rounding is None:
                raise ValueError("This screen type requires the argument rounding")

        self.pixel_aspect = pixel_aspect
        self.rounding = rounding

        # Get the filter tile image
        if self.screen_type == ScreenType.CRT_MONITOR:
            self.filter_tile = crt_monitor(
                size=self.pixel_size,
                padding=self.pixel_padding,
                direction=self.direction
            )
        elif self.screen_type == ScreenType.CRT_TV:
            self.filter_tile = crt_tv(
                size=self.pixel_size,
                padding=self.pixel_padding,
                direction=self.direction,
                aspect=self.pixel_aspect,
                rounding=self.rounding
            )
        else:  # Default to LCD
            self.filter_tile = lcd(
                size=self.pixel_size,
                padding=self.pixel_padding,
                direction=self.direction,
                aspect=self.pixel_aspect,
                rounding=self.rounding
            )

        self.strength = strength

        # Pre-compute a tiled filter image
        self.filter_raw = helpers.tile_image(self.filter_tile, self.size)

        # Pre-computed adjusted filter image
        self.filter = helpers.lighten_image(self.filter_raw, 1 - self.strength)

    # Apply the filter to a desired image
    def apply(self, image):
        if image.size != self.size:
            raise ValueError(f"Input image size \"{image.size}\" does not match filter size \"{self.size}\"")

        result = ImageChops.multiply(image, self.filter)

        return result
