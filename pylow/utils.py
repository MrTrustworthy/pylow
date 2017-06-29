from collections import namedtuple
from enum import unique, Enum
from typing import List, Union, Any

Number = Union[int, float]

ColumnNameCollection = namedtuple('ColumnNameCollection', ['x', 'y', 'color', 'size'])


def make_unique_string_list(content: List[str]):
    s = set()
    new = []
    for word in content:
        i = 0
        while word in s:
            word = f' {word}' if i % 2 == 0 else f'{word} '
            i += 1
        s.add(word)
        new.append(word)
    return new


def unique_list(content: List[Any]) -> List[Any]:
    """ Can't rely on sets to preserve order """
    out = []
    for c in content:
        if c not in out:
            out.append(c)
    return out


def reverse_lerp(point: Number, pointlist: List[Number]) -> float:
    _min, _max = min(pointlist), max(pointlist)
    value_range = _max - _min
    abs_in_range = point - _min
    relative_in_range = (abs_in_range / value_range)
    return relative_in_range


MarkInfo = namedtuple('MarkInfo', ['glyph_name', 'glyph_size_factor'])


@unique
class MarkType(Enum):
    CIRCLE = MarkInfo('Circle', 10)
    BAR = MarkInfo('VBar', 0.25)
    LINE = MarkInfo('Line', 1)
