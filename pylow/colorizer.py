from typing import List, Tuple
from itertools import cycle
from .avp import AVP


BLUE = '#1f77b4'
ORANGE = '#ff7f0e'
GREEN = '#2ca02c'
RED = '#d62728'
PURPLE = '#9467bd'
BROWN = '#8c564b'
PINK = '#e377c2'
GRAY = '#7f7f7f'
OLIVE = '#bcbd22'
CYAN = '#17becf'

ALL_COLORS = [BLUE, ORANGE, GREEN, RED, PURPLE, BROWN, PINK, GRAY, OLIVE, CYAN]
DEFAULT_COLOR = BLUE


def adjust_brightness(color: str, amount: float):
    # -1 == black, 0 == equal, 1 == white

    r, g, b = to_rgb(color)
    r = to_valid_rgb(r + (r * amount))
    g = to_valid_rgb(g + (g * amount))
    b = to_valid_rgb(b + (b * amount))
    return to_hex(r, g, b)


def to_hex(r: int, g: int, b: int) -> str:
    return '#{0:02x}{1:02x}{2:02x}'.format(r, g, b)


def to_rgb(color: str) -> Tuple[int]:
    assert isinstance(color, str) and color.startswith('#') and len(color) == 7, 'Color must be a string'
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


def to_valid_rgb(color: int) -> int:
    return int(max(min(color, 255), 0))


def get_colors_for_color_separators(col_seps: List['AVP']) -> None:
    all_values = set(avp.val for avp in col_seps)
    val_to_color = dict(zip(all_values, cycle(ALL_COLORS)))
    for avp in col_seps:
        yield AVP(avp.attr, val_to_color[avp.val])
