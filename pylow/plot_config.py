from collections import namedtuple


ConfigAttribute = namedtuple('Attribute', ['col_name', 'aspect_type'])

class PlotConfig:

    def __init__(self):

        # all non-writeable properties to ensure lists don't get switched out
        self._columns = []
        self._rows = []
        self._aggregations = []
        self._draw_types = []
        self._colors = []

    @property
    def columns(self):
        return self._columns

    @property
    def rows(self):
        return self._rows

    @property
    def aggregations(self):
        return self._aggregations

    @property
    def draw_types(self):
        return self._draw_types

    @property
    def colors(self):
        return self._colors

    def is_valid_config(self):
        # TODO Validate by checking if equal amounts of rows & colors or smth are there
        return True

    def clear(self, *, property=None):
        for prop in vars(self).keys():
            # remove starting underscore to access the property instead of the attribute
            prop = prop[1:]
            if property is None or property == prop:
                getattr(self, prop).clear()

    @classmethod
    def from_dict(cls, _dict):
        pc = cls()
        for key, value in _dict.items():
            for item in value:
                getattr(pc, key).append(item)
        return pc
