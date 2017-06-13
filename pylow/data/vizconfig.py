from itertools import chain
from typing import List, Union

from pylow.utils import unique_list, MarkType
from .attributes import Attribute, Dimension, Measure

Number = Union[int, float]


class VizConfig:
    def __init__(self) -> None:

        # non-writeable properties to ensure lists don't get switched out
        self._columns = []  # type: List[Attribute]
        self._rows = []  # type: List[Attribute]
        self.color = None  # type: Attribute
        self.color_sep = None  # type: Attribute
        self.size = None  # type: Attribute
        self.mark_type = None  # type: MarkType

    @classmethod
    def from_dict(cls, _dict: dict) -> 'VizConfig':
        vc = cls()
        vc.columns.extend(_dict['columns'])
        vc.rows.extend(_dict['rows'])

        color = _dict.get('color', None)
        if color in vc.columns_and_rows or isinstance(color, Measure):
            vc.color = color
        else:
            vc.color_sep = color

        vc.size = _dict.get('size', None)
        vc.mark_type = _dict.get('mark_type', MarkType.CIRCLE)
        return vc

    @property
    def columns_and_rows(self) -> List[Attribute]:
        return self.columns + self.rows

    @property
    def columns(self) -> List[Attribute]:
        return self._columns

    @property
    def rows(self) -> List[Attribute]:
        return self._rows

    @property
    def dimensions(self) -> List[Attribute]:
        return unique_list(self._find_attrs(chain(self.columns, self.rows, [self.color, self.color_sep]), Dimension))

    @property
    def measures(self) -> List[Attribute]:
        return unique_list(self._find_attrs(chain(self.columns, self.rows, [self.color, self.color_sep]), Measure))

    @property
    def column_dimensions(self) -> List[Attribute]:
        return self._find_attrs(self.columns, Dimension)

    @property
    def row_dimensions(self) -> List[Attribute]:
        return self._find_attrs(self.rows, Dimension)

    @property
    def column_measures(self) -> List[Attribute]:
        return self._find_attrs(self.columns, Measure)

    @property
    def row_measures(self) -> List[Attribute]:
        return self._find_attrs(self.rows, Measure)

    @property
    def all_attrs(self):
        return list(chain(self.dimensions, self.measures))

    @property
    def previous_columns(self):
        return self.columns[:-1]

    @property
    def last_column(self):
        return self.columns[-1]

    @property
    def previous_rows(self):
        return self.rows[:-1]

    @property
    def last_row(self):
        return self.rows[-1]

    def _find_attrs(self, iterable: List[Attribute], attr_class: Attribute):
        return list(filter(lambda elem: isinstance(elem, attr_class), iterable))

    def get_glyph_size(self, size: Number) -> Number:
        """Map a 'generic size value' to the concrete size for a given glyph/mark type"""
        return size * self.mark_type.value.glyph_size_factor

    def __str__(self) -> str:
        col = f'{len(self.column_dimensions)}d{len(self.column_measures)}m'
        row = f'{len(self.row_dimensions)}d{len(self.row_measures)}m'
        size = f'size{type(self.size).__name__[0]}'
        color = f'size{type(self.color).__name__[0]}'
        return '_'.join(['CONF', col, row, size, color])
