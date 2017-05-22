from collections import namedtuple
from itertools import chain


class Attribute:

    def __init__(self, col_name):
        self.col_name = col_name

    def __str__(self):
        return self.col_name

    def __repr__(self):
        return f'<plot_config.{type(self).__name__}: {self.col_name}>'


class Dimension(Attribute):

    def __init__(self, col_name: str):
        super().__init__(col_name)


class Measure(Attribute):

    def __init__(
        self,
        col_name: str,
        *,
        aggregation: str='sum',
        draw_type: str='plot',
        color: str='b',
        double_axis: bool=False,
    )-> None:
        super().__init__(col_name)
        self.aggregation = aggregation
        self.draw_type = draw_type
        self.color = color
        self.double_axis = double_axis  # TODO use this


class PlotConfig:

    def __init__(self):

        # all non-writeable properties to ensure lists don't get switched out
        self._columns = []
        self._rows = []
        self.colors = []
        self.tooltips = []

    @property
    def columns(self) -> list:
        return self._columns

    @property
    def rows(self) -> list:
        return self._rows

    @property
    def dimensions(self) -> list:
        return self._find_attrs(chain(self.columns, self.rows), Dimension)

    @property
    def measures(self) -> list:
        return self._find_attrs(chain(self.columns, self.rows), Measure)

    @property
    def column_dimensions(self) -> list:
        return self._find_attrs(self.columns, Dimension)

    @property
    def row_dimensions(self) -> list:
        return self._find_attrs(self.rows, Dimension)

    @property
    def column_measures(self) -> list:
        return self._find_attrs(self.columns, Measure)

    @property
    def row_measures(self) -> list:
        return self._find_attrs(self.rows, Measure)

    def _find_attrs(self, iterable, attr_class):
        return list(filter(lambda elem: isinstance(elem, attr_class), iterable))

    def is_valid_config(self):
        # TODO Validate by checking if equal amounts of measures & colors or smth are there
        return True

    def clear(self, *, property: str = None) -> None:
        for prop in vars(self).keys():
            # remove starting underscore to access the property instead of the attribute
            prop = prop[1:]
            if property is None or property == prop:
                getattr(self, prop).clear()

    @classmethod
    def from_dict(cls, _dict: dict) -> 'PlotConfig':
        pc = cls()
        pc.columns.extend(_dict['columns'])
        pc.rows.extend(_dict['rows'])
        return pc
