import math
from PIL import Image, ImageDraw

import helpers
from constants import Direction, ScreenType


def lcd(size, aspect, padding, rounding, direction):
    # Get main pixel dimensions (float, used in calculations)
    if direction == Direction.VERTICAL:
        width = size
        height = size / aspect
    else:
        height = size
        width = size * aspect

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
    if direction == Direction.VERTICAL:
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
    else:
        rg_boundary_y = round(height / 3)
        gb_boundary_y = round((2 * height) / 3)

        if padding_px == 0:
            red_start = (0, 0)
            red_end = (width_px - 1, rg_boundary_y - 1)

            green_start = (0, rg_boundary_y)
            green_end = (width_px - 1, gb_boundary_y - 1)

            blue_start = (0, gb_boundary_y)
            blue_end = (width_px - 1, height_px - 1)
        else:
            red_start = (padding_left, padding_left)
            red_end = (
                max((width_px - padding_right) - 1, red_start[0]),
                max((rg_boundary_y - padding_right) - 1, red_start[1])
            )

            green_start = (padding_left, rg_boundary_y + padding_left)
            green_end = (
                max((width_px - padding_right) - 1, green_start[0]),
                max((gb_boundary_y - padding_right) - 1, green_start[1])
            )

            blue_start = (padding_left, gb_boundary_y + padding_left)
            blue_end = (
                max((width_px - padding_right) - 1, blue_start[0]),
                max((height_px - padding_right) - 1, blue_start[1])
            )

        color_size_px = red_end[1] - red_start[1]

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

    return filter_image


def crt_tv(size, aspect, padding, rounding, direction):
    # Get the first half of the filter
    single_pixel = lcd(size=size,
                       aspect=aspect,
                       padding=padding,
                       rounding=rounding,
                       direction=direction
                       )

    # Figure out the dimensions for the new filter
    if direction == Direction.VERTICAL:
        new_size = (single_pixel.width * 2, single_pixel.height)
    else:
        new_size = (single_pixel.width, single_pixel.height * 2)

    # Make new image to paste old one onto
    both_pixels = Image.new("RGB", new_size, color=(0, 0, 0))

    # Paste the first pixel
    both_pixels.paste(single_pixel, (0, 0))

    # Paste the second pixel in two parts
    if direction == Direction.VERTICAL:
        split_y = round(both_pixels.height / 2)
        both_pixels.paste(single_pixel, (single_pixel.width, split_y))
        both_pixels.paste(single_pixel, (single_pixel.width, split_y - single_pixel.height))
    else:
        split_x = round(both_pixels.width / 2)
        both_pixels.paste(single_pixel, (split_x, single_pixel.height))
        both_pixels.paste(single_pixel, (split_x - single_pixel.width, single_pixel.height))

    return both_pixels


def crt_monitor(size, padding, direction):
    # Get width and height from dot size (float, used for calculations)
    if direction == Direction.HORIZONTAL:
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
    else:
        height = size * 3
        width = size * math.sqrt(3)

        # Get integer divisions for dot placement
        height_divs = (
            0,
            round(height * (1 / 6)),
            round(height * (2 / 6)),
            round(height * (3 / 6)),
            round(height * (4 / 6)),
            round(height * (5 / 6)),
            round(height)
        )
        width_divs = (
            0,
            round(width / 2),
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

    # Draw the dots
    if direction == Direction.HORIZONTAL:
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
    else:
        filter_draw.ellipse(
            helpers.get_centered_dimensions((width_divs[0], height_divs[0]), (dot_size, dot_size)),
            fill=(255, 0, 0)
        )
        filter_draw.ellipse(
            helpers.get_centered_dimensions((width_divs[2], height_divs[0]), (dot_size, dot_size)),
            fill=(255, 0, 0)
        )
        filter_draw.ellipse(
            helpers.get_centered_dimensions((0, height_divs[6]), (dot_size, dot_size)),
            fill=(255, 0, 0)
        )
        filter_draw.ellipse(
            helpers.get_centered_dimensions((width_divs[2], height_divs[6]), (dot_size, dot_size)),
            fill=(255, 0, 0)
        )
        filter_draw.ellipse(
            helpers.get_centered_dimensions((width_divs[1], height_divs[3]), (dot_size, dot_size)),
            fill=(255, 0, 0)
        )

        # Draw green dots
        filter_draw.ellipse(
            helpers.get_centered_dimensions((width_divs[0], height_divs[2]), (dot_size, dot_size)),
            fill=(0, 255, 0)
        )
        filter_draw.ellipse(
            helpers.get_centered_dimensions((width_divs[2], height_divs[2]), (dot_size, dot_size)),
            fill=(0, 255, 0)
        )
        filter_draw.ellipse(
            helpers.get_centered_dimensions((width_divs[1], height_divs[5]), (dot_size, dot_size)),
            fill=(0, 255, 0)
        )

        # Draw blue dots
        filter_draw.ellipse(
            helpers.get_centered_dimensions((width_divs[1], height_divs[1]), (dot_size, dot_size)),
            fill=(0, 0, 255)
        )
        filter_draw.ellipse(
            helpers.get_centered_dimensions((width_divs[0], height_divs[4]), (dot_size, dot_size)),
            fill=(0, 0, 255)
        )
        filter_draw.ellipse(
            helpers.get_centered_dimensions((width_divs[2], height_divs[4]), (dot_size, dot_size)),
            fill=(0, 0, 255)
        )


    return filter_image
