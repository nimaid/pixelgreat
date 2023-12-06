from enum import Enum

DESCRIPTION = "A highly realistic RGB pixel filter"


class Direction(Enum):
    VERTICAL = 0
    HORIZONTAL = 1


class ScreenType(Enum):
    LCD = 0
    CRT_TV = 1
    CRT_MONITOR = 2


DEFAULTS = {
    "screen_type": ScreenType.LCD,
    "pixel_padding": {
        "LCD": 0.25,
        "CRT_TV": 0.25,
        "CRT_MONITOR": 0.1
    },
    "direction": {
        "LCD": Direction.VERTICAL,
        "CRT_TV": Direction.VERTICAL,
        "CRT_MONITOR": Direction.HORIZONTAL
    },
    "washout": {
        "LCD": 0.1,
        "CRT_TV": 0.5,
        "CRT_MONITOR": 0.5
    },
    "blur": {
        "LCD": 0,
        "CRT_TV": 0.5,
        "CRT_MONITOR": 0.75
    },
    "bloom_size": 0.5,
    "pixel_aspect": 1.0,
    "rounding": {
        "LCD": 0,
        "CRT_TV": 0.5,
        "CRT_MONITOR": 0
    },
    "scanline_spacing": 0.79,
    "scanline_size": 0.75,
    "scanline_blur": 0.25,
    "scanline_strength": {
        "LCD": 0,
        "CRT_TV": 1,
        "CRT_MONITOR": 0.5
    },
    "bloom_strength": 1.0,
    "grid_strength": 1.0,
    "pixelate": True,
    "output_scale": 1.0
}


