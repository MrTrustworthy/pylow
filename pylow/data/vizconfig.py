from itertools import chain
from typing import List, TypeVar, Optional, Iterable, Union, Type

from pylow.data.attributes import Attribute, Dimension, Measure
from pylow.logger import log
from pylow.utils import unique_list, MarkType

Number = Union[int, float]
T = TypeVar('T')


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
        log(self, 'Initializing VizConfig')

    @classmethod
    def from_dict(cls, _dict: dict) -> 'VizConfig':
        """ Factory to create a VizConfig based on a dict object

        Mainly used for testing right now
        """

        log('#VizConfig_class', 'Creating VizConfig from dict')

        columns = _dict.get('columns', [])
        rows = _dict.get('rows', [])
        color = _dict.get('color', None)
        size = _dict.get('size', None)
        mark_type = _dict.get('mark_type', MarkType.CIRCLE)

        vc = cls(columns, rows, color, size, mark_type)

        return vc

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
    def x_separators(self) -> List[Attribute]:
        if len(self.columns) == 0:
            return []
        return self.columns[:-1]

    @property
    def x_data(self) -> Attribute:
        if len(self.columns) == 0:
            raise NoSuchAttributeException('No Attributes in self.columns')
        return self.columns[-1]

    @property
    def y_separators(self) -> List[Attribute]:
        if len(self.rows) == 0:
            return []
        return self.rows[:-1]

    @property
    def y_data(self) -> Attribute:
        if len(self.rows) == 0:
            raise NoSuchAttributeException('No Attributes in self.rows')
        return self.rows[-1]

    @staticmethod
    def find_attrs(iterable: Iterable[Attribute], attr_class: Type[T]) -> List[T]:
        return [attr for attr in iterable if isinstance(attr, attr_class)]

    def __repr__(self) -> str:
        """ Returns a String describing the config, such as CONF_1d0m_1d1m_sizeDX_colDX_circle
        """

        col = f'{len(self.find_attrs(self.columns, Dimension))}d{len(self.find_attrs(self.columns, Measure))}m'
        row = f'{len(self.find_attrs(self.rows, Dimension))}d{len(self.find_attrs(self.rows, Measure))}m'

        cols_and_rows = list(chain(self.columns, self.rows))
        x_val_size = "X" if self.size not in cols_and_rows else ""
        size = f'size{type(self.size).__name__[0].upper()}{x_val_size}'

        x_val_col = "X" if self.color not in cols_and_rows else ""
        color = f'col{type(self.color).__name__[0].upper()}{x_val_col}'

        mark = self.mark_type.value.glyph_name.lower()
        return '_'.join(['CONF', col, row, size, color, mark])
