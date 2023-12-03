from enum import Enum


DESCRIPTION = "A hyper-realistic RGB pixel filter"


class Direction(Enum):
    VERTICAL = 0
    HORIZONTAL = 1


class ScreenType(Enum):
    LCD = 0
    CRT_TV = 1
    CRT_MONITOR = 2
