from itertools import chain
from typing import List, Union, TypeVar, Optional

from pylow.utils import unique_list, MarkType
from .attributes import Attribute, Dimension, Measure

Number = Union[int, float]
AttributeSubclass = TypeVar('AttributeSubclass', Dimension, Measure)


class NoSuchAttributeException(Exception):
    pass


class VizConfig:
    """ The VizConfig holds informations about the composition of visualizations/plots

    Any information that is needed for the data aggregation (dimensions, measures)
    and plot generation (rows, columns) as well as styling (glyphs, colors, sizes, ...) is encapsulated here.

    This class is vital for data exploration by allowing an user to modify the viz that is generated.
    """

    def __init__(
            self,
            columns: List[Attribute],
            rows: List[Attribute],
            color: Optional[Attribute],
            size: Optional[Attribute],
            mark_type: MarkType
    ) -> None:
        # non-writeable properties to ensure lists don't get switched out
        self._columns = columns  # type: List[Attribute]
        self._rows = rows  # type: List[Attribute]
        self.color = color  # type: Optional[Attribute]
        self.size = size  # type: Optional[Attribute]
        self.mark_type = mark_type  # type: MarkType

    @classmethod
    def from_dict(cls, _dict: dict) -> 'VizConfig':
        """ Factory to create a VizConfig based on a dict object

        Mainly used for testing right now
        """
        columns = _dict.get('columns', [])
        rows = _dict.get('rows', [])
        color = _dict.get('color', None)
        size = _dict.get('size', None)
        mark_type = _dict.get('mark_type', MarkType.CIRCLE)

        vc = cls(columns, rows, color, size, mark_type)

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
    def dimensions(self) -> List[Dimension]:
        return unique_list(self.find_attrs(chain(self.columns, self.rows, [self.color, self.size]), Dimension))

    @property
    def measures(self) -> List[Measure]:
        return unique_list(self.find_attrs(chain(self.columns, self.rows, [self.color, self.size]), Measure))

    @property
    def column_dimensions(self) -> List[Dimension]:
        return self.find_attrs(self.columns, Dimension)

    @property
    def row_dimensions(self) -> List[Dimension]:
        return self.find_attrs(self.rows, Dimension)

    @property
    def column_measures(self) -> List[Measure]:
        return self.find_attrs(self.columns, Measure)

    @property
    def row_measures(self) -> List[Measure]:
        return self.find_attrs(self.rows, Measure)

    @property
    def all_attrs(self):
        return list(chain(self.dimensions, self.measures))

    @property
    def previous_columns(self) -> List[Attribute]:
        if len(self.columns) == 0:
            return []
        return self.columns[:-1]

    @property
    def last_column(self) -> Attribute:
        if len(self.columns) == 0:
            raise NoSuchAttributeException('No Attributes in self.columns')
        return self.columns[-1]

    @property
    def previous_rows(self) -> List[Attribute]:
        if len(self.rows) == 0:
            return []
        return self.rows[:-1]

    @property
    def last_row(self) -> Attribute:
        if len(self.rows) == 0:
            raise NoSuchAttributeException('No Attributes in self.rows')
        return self.rows[-1]

    @staticmethod
    def find_attrs(iterable: List[Attribute], attr_class: AttributeSubclass) -> List[AttributeSubclass]:
        return list(filter(lambda elem: isinstance(elem, attr_class), iterable))

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        """ Returns a String describing the config, such as CONF_1d0m_1d1m_sizeDX_colDX_circle
        """

        col = f'{len(self.column_dimensions)}d{len(self.column_measures)}m'
        row = f'{len(self.row_dimensions)}d{len(self.row_measures)}m'

        x_val_size = "X" if self.size not in self.columns_and_rows else ""
        size = f'size{type(self.size).__name__[0].upper()}{x_val_size}'

        x_val_col = "X" if self.color not in self.columns_and_rows else ""
        color = f'col{type(self.color).__name__[0].upper()}{x_val_col}'

        mark = self.mark_type.value.glyph_name.lower()
        return '_'.join(['CONF', col, row, size, color, mark])
