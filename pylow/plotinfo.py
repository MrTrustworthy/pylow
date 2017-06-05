from collections import namedtuple
from itertools import chain
from typing import Dict, List, Tuple

from .colorizer import DEFAULT_COLOR
from .plot_config import Attribute
# from .aggregator import Aggregator

# attribute_value pair
AVP = namedtuple('AVP', ['attr', 'val'])


class PlotInfoBuilder:
    _plotinfo_cache = []

    @classmethod
    def create_all_plotinfos(cls, data: List[List[AVP]], aggregator: 'Aggregator'):
        """ The single public interface of PlotInfoBuilder

        Will take a list of AVP-Lists and create a list of PlotInfo objects from them
        """
        for dataset in data:
            cls._make_plot_info(dataset, aggregator)

        output = cls._plotinfo_cache[:]
        cls._plotinfo_cache.clear()

        # sort data so that dimensions and measures stay grouped
        output.sort(key=lambda x: [avp.val for avp in chain(x.y_seps[::-1], x.x_seps[::-1])])
        return output

    @classmethod
    def _make_plot_info(cls, plot_data: List[AVP], aggregator: 'Aggregator') -> None:
        """ Gathers the data necessary for a single PlotInfo object and creates it

        Will not return an object but rather put it into the _plotinfo_cache
        """
        find_index = aggregator.all_attrs.index

        x_coords = [plot_data[find_index(aggregator.last_column)]]
        y_coords = [plot_data[find_index(aggregator.last_row)]]
        x_seps = [plot_data[find_index(col)] for col in aggregator.previous_columns]
        y_seps = [plot_data[find_index(col)] for col in aggregator.previous_rows]

        cls._create_new_or_update(x_coords, y_coords, x_seps, y_seps)

    @classmethod
    def _create_new_or_update(
        cls,
        x_coords: List[AVP] = None,
        y_coords: List[AVP] = None,
        x_seps: List[AVP] = None,
        y_seps: List[AVP] = None
    ) -> None:
        """ Creates a new PlotInfo object or, if one already exists for those plot separators, extends it"""

        # create new object and determine of there are already fitting existing objects
        new_plotinfo = PlotInfo(x_coords, y_coords, x_seps, y_seps)
        existing_plotinfos = list(filter(lambda ppi: ppi.would_be_in_same_plot(new_plotinfo), cls._plotinfo_cache))

        if len(existing_plotinfos) == 0:
            # use the new object
            cls._plotinfo_cache.append(new_plotinfo)
        elif len(existing_plotinfos) == 1:
            # use an existing object and discard the newly created one
            existing = existing_plotinfos[0]
            existing.x_coords.extend(x_coords)
            existing.y_coords.extend(y_coords)
        else:
            # There should never be more than 1 existing object
            assert False, f'Already have {len(existing_plotinfos)} objects'


class PlotInfo:

    def __init__(
        self,
        x_coords: List[AVP] = None,
        y_coords: List[AVP] = None,
        x_seps: List[AVP] = None,
        y_seps: List[AVP] = None,
        color_seps: List[AVP] = None
    ):
        assert len(x_coords) == len(y_coords)
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.x_seps = x_seps
        self.y_seps = y_seps
        self.color_seps = color_seps
        self._colors = None  # will be drawn from property
        self._sizes = None  # will be drawn from property

    @property
    def colors(self):
        return self._colors if self._colors is not None else [AVP(None, DEFAULT_COLOR)] * len(self.x_coords)

    @colors.setter
    def colors(self, val):
        assert val is None or len(val) == len(self.x_coords)
        self._colors = val

    @property
    def sizes(self):
        return self._sizes if self._sizes is not None else [AVP(None, 1)] * len(self.x_coords)

    @sizes.setter
    def sizes(self, val):
        assert val is None or len(val) == len(self.x_coords)
        self._sizes = val

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
