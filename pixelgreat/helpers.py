import os

# Define commonly used helper functions


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

    return (start, end)
