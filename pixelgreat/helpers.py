import os
import math
from PIL import Image


# General purpose text input stripper
def strip_all(input_text):
    return input_text.strip().strip("\n").strip("\r").strip()


# Makes sure a string represents a valid, existing file
# This can be used with argparse as a valid argument type
def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise FileNotFoundError(string)


# A short function to clip a value to a range
def clip(value, min_value, max_value):
    return min(max(value, min_value), max_value)


# A function to give absolute bounding coordinates for a specified center point and object size
def get_centered_dimensions(center, size):
    start = (
        center[0] - (size[0] / 2),
        center[1] - (size[1] / 2),
    )
    end = (
        center[0] + (size[0] / 2),
        center[1] + (size[1] / 2),
    )

    return start, end


# A function to round to a given "division", like 0.5 instead of the default 1.0
def round_to_division(value, division=1.0):
    inverse = 1/division
    return round(value * inverse) / inverse


# Tile a PIL Image to fit a given frame size
def tile_image(image_tile, size, background_color=(0, 0, 0), count=None):
    # TODO: Fix this being misaligned with pixelate somehow
    # TODO: Maybe add the option to specify a count tuple?
    new_image = Image.new(image_tile.mode, size, color=background_color)

    if count is None:
        # Position pastes based on tile size
        x_count = math.ceil(new_image.width / image_tile.width)
        y_count = math.ceil(new_image.height / image_tile.height)

        for x in range(x_count):
            for y in range(y_count):
                new_image.paste(
                    image_tile,
                    (
                        x * image_tile.width,
                        y * image_tile.height
                    )
                )
    else:
        # Position pastes based on count tuple (can be a float)
        x_count, y_count = count
        x_count_int = math.ceil(x_count)
        y_count_int = math.ceil(y_count)
        for x in range(x_count_int):
            for y in range(y_count_int):
                new_image.paste(
                    image_tile,
                    (
                        round((x / x_count) * new_image.width),
                        round((y / y_count) * new_image.height)
                    )
                )

    return new_image


# Mix a PIL image with white
def lighten_image(image, factor):
    if factor <= 0:
        return image

    white_image = Image.new(image.mode, image.size, (255, 255, 255))

    if factor >= 1:
        return white_image

    new_image = Image.blend(image, white_image, factor)

    return new_image
