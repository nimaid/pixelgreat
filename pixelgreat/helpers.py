import os
import math
import glob
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
    new_image = Image.new(image_tile.mode, size, color=background_color)

    if count is None:
        # Position pastes based on tile size
        x_count = math.ceil(new_image.width / image_tile.width)
        y_count = math.ceil(new_image.height / image_tile.height)

        for x in range(x_count):
            for y in range(y_count):
                new_image.paste(image_tile, (x * image_tile.width, y * image_tile.height))
    else:
        # Position pastes based on count tuple (can be a float)
        x_count, y_count = count
        x_count_int = math.ceil(x_count)
        y_count_int = math.ceil(y_count)
        for x in range(x_count_int):
            for y in range(y_count_int):
                tile_start = (
                        round((x / x_count) * new_image.width),
                        round((y / y_count) * new_image.height)
                    )
                tile_end = (
                    round(((x + 1) / x_count) * new_image.width),
                    round(((y + 1) / y_count) * new_image.height)
                )

                target_size = (
                    tile_end[0] - tile_start[0],
                    tile_end[1] - tile_start[1]
                )

                if image_tile.size == target_size:
                    this_tile = image_tile
                else:
                    this_tile = image_tile.resize(target_size, resample=Image.Resampling.LANCZOS)

                new_image.paste(this_tile, tile_start)

    return new_image


# Mix a PIL image with white
def mix_color_with_image(image, color, factor):
    if factor <= 0:
        return image

    white_image = Image.new(image.mode, image.size, color=color)

    if factor >= 1:
        return white_image

    new_image = Image.blend(image, white_image, factor)

    return new_image


# If a value is out of range, raise an exception
def assert_value_in_range(value, minimum=None, maximum=None, message=None):
    raise_error = False
    if minimum is not None:
        if value < minimum:
            raise_error = True
    if maximum is not None:
        if value > maximum:
            raise_error = True

    if raise_error:
        if message is None:
            if minimum is not None and maximum is not None:
                raise ValueError(f"Expected a value between {minimum} and {maximum}, got {value}")
            elif minimum is not None:
                raise ValueError(f"Expected a value no less than {minimum}, got {value}")
            elif maximum is not None:
                raise ValueError(f"Expected a value no more than {maximum}, got {value}")
        else:
            raise ValueError(message.format(min=minimum, max=maximum, val=value))


# Helper function to get info from a sequenced image filename
def parse_sequenced_image_name(image_file):
    main_path, image_filename = os.path.split(image_file)
    file_basename, ext = os.path.splitext(image_filename)
    number = ""

    for x in file_basename[::-1]:
        if x.isdigit():
            number += x
        else:
            break

    if len(number) > 0:
        return {"error": None,
                "digits": len(number),
                "image_number": int(number),
                "prefix": os.path.join(main_path, "".join(file_basename.split(number)[:-1])),
                "ext": ext}
    else:
        return {"error": "No trailing digits found."}


def get_all_images_in_sequence(image_file):
    info = parse_sequenced_image_name(image_file)

    if info["error"] is None:
        return {
            "files": glob.glob(info["prefix"] + ("[0-9]" * info["digits"]) + info["ext"]),
            "digits": info["digits"],
            "ext": info["ext"],
            "prefix": info["prefix"]
        }
    else:
        return None
