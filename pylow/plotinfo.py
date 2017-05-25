from collections import namedtuple
from typing import Dict, List, Tuple
from itertools import chain

from .plot_config import Attribute

# attribute_value pair
AVP = namedtuple('AVP', ['attr', 'val'])


class PlotInfo:

    _point_list = []  # TODO add context manager to clear automatically?

    def __init__(
        self,
        x_coords: List[AVP] = None,
        y_coords: List[AVP] = None,
        x_seps: List[AVP] = None,
        y_seps: List[AVP] = None,
        colors: List[AVP] = None
    ):
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.x_seps = x_seps
        self.y_seps = y_seps
        self.colors = colors

    @classmethod
    def create_new_or_update(
        cls,
        x_coords: List[AVP] = None,
        y_coords: List[AVP] = None,
        x_seps: List[AVP] = None,
        y_seps: List[AVP] = None
        # colors: List[AVP] = None
    ):
        new = cls(x_coords, y_coords, x_seps, y_seps)
        existing_objects = list(filter(lambda ppi: ppi.would_be_in_same_plot(new), cls._point_list))
        if len(existing_objects) == 0:
            cls._point_list.append(new)
            return new
        elif len(existing_objects) == 1:
            existing = existing_objects[0]
            existing.x_coords.extend(x_coords)
            existing.y_coords.extend(y_coords)
            # existing.colors.extend(colors)
            return existing
        assert False

    @classmethod
    def clear_point_cache(cls) ->None:
        cls._point_list.clear()

    @property
    def all(self):
        return chain(self.x_coords, self.y_coords, self.x_seps, self.y_seps)

    def would_be_in_same_plot(self, other: 'PlotInfo'):
        return self.x_seps == other.x_seps and self.y_seps == other.y_seps

    def variations_of(self, attribute: Attribute):
        relevant_values = [avp.val for avp in self.all if avp.attr == attribute]
        return set(relevant_values)

    def __str__(self):
        return f'<{[x.val for x in self.x_coords]}:{[x.val for x in self.y_coords]}>(seps_x:{self.x_seps}, seps_y:{self.y_seps})'

    def __repr__(self):
        return str(self)
