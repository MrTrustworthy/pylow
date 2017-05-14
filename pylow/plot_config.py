from collections import namedtuple

Dimension = namedtuple('Dimension', ['col_name'])


class Measure:

    def __init__(
        self,
        col_name: str,
        *,
        aggregation: str='sum',
        draw_type: str='plot',
        color: str='b',
        options: dict={}
    )-> None:
        self.col_name = col_name
        self.aggregation = aggregation
        self.draw_type = draw_type
        self.color = color
        self.options = options.copy()


class PlotConfig:

    def __init__(self):

        # all non-writeable properties to ensure lists don't get switched out
        self._dimensions = []
        self._measures = []

    @property
    def dimensions(self) -> list:
        return self._dimensions

    @property
    def measures(self) -> list:
        return self._measures

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
        for key, value in _dict.items():
            for item in value:
                getattr(pc, key).append(item)
        return pc
