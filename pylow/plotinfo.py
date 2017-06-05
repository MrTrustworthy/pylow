from itertools import chain
from typing import Dict, List, Tuple, Any, Union

from .colorizer import DEFAULT_COLOR, get_colors_for_color_separators
from .plot_config import Attribute
# from .aggregator import Aggregator
from .avp import AVP


class PlotInfoBuilder:
    _plotinfo_cache = []

    @classmethod
    def create_all_plotinfos(cls, data: List[List[AVP]], config: 'VizConfig'):
        """ The single public interface of PlotInfoBuilder

        Will take a list of AVP-Lists and create a list of PlotInfo objects from them
        """
        for dataset in data:
            cls._make_plot_info(dataset, config)

        output = cls._plotinfo_cache[:]
        cls._plotinfo_cache.clear()

        # sort data so that dimensions and measures stay grouped
        output.sort(key=lambda x: [avp.val for avp in chain(x.y_seps[::-1], x.x_seps[::-1])])
        return output

    @classmethod
    def _make_plot_info(cls, plot_data: List[AVP], config: 'VizConfig') -> None:
        """ Gathers the data necessary for a single PlotInfo object and creates it

        Will not return an object but rather put it into the _plotinfo_cache
        """
        find_index = config.all_attrs.index

        x_coords = [plot_data[find_index(config.last_column)]]
        y_coords = [plot_data[find_index(config.last_row)]]
        x_seps = [plot_data[find_index(col)] for col in config.previous_columns]
        y_seps = [plot_data[find_index(col)] for col in config.previous_rows]

        color_seps = [plot_data[find_index(config.color_sep)]] if config.color_sep is not None else None

        used_indicies = set(find_index(col) for col in config.rows + config.columns)
        all_indicies = set(range(len(plot_data)))
        additional_data_indicies = all_indicies - used_indicies
        additional_data = [plot_data[i] for i in additional_data_indicies]

        cls._create_new_or_update(x_coords, y_coords, x_seps, y_seps, color_seps, additional_data)

    @classmethod
    def _create_new_or_update(
        cls,
        x_coords: List[AVP],
        y_coords: List[AVP],
        x_seps: List[AVP],
        y_seps: List[AVP],
        color_seps: List[AVP],
        additional_data: List[AVP]
    ) -> None:
        """ Creates a new PlotInfo object or, if one already exists for those plot separators, extends it"""

        # create new object and determine of there are already fitting existing objects
        new_plotinfo = PlotInfo(x_coords, y_coords, x_seps, y_seps, color_seps, additional_data)
        existing_plotinfos = list(filter(lambda ppi: ppi.would_be_in_same_plot(new_plotinfo), cls._plotinfo_cache))

        if len(existing_plotinfos) == 0:
            # use the new object
            cls._plotinfo_cache.append(new_plotinfo)
        elif len(existing_plotinfos) == 1:
            # use an existing object and discard the newly created one
            existing = existing_plotinfos[0]
            existing.x_coords.extend(x_coords)
            existing.y_coords.extend(y_coords)
            existing.additional_data.extend(additional_data)
            if color_seps is not None:
                existing.color_seps.extend(color_seps)

        else:
            # There should never be more than 1 existing object
            assert False, f'Already have {len(existing_plotinfos)} objects'


class PlotInfo:

    def __init__(
        self,
        x_coords: List[AVP],
        y_coords: List[AVP],
        x_seps: List[AVP],
        y_seps: List[AVP],
        color_seps: List[AVP],
        additional_data: List[AVP]
    ):
        assert len(x_coords) == len(y_coords)
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.x_seps = x_seps
        self.y_seps = y_seps
        self.color_seps = color_seps
        self.additional_data = additional_data
        self._colors = None  # will be drawn from property
        self._sizes = None  # will be drawn from property

    @property
    def colors(self):
        if self._colors is not None:
            return self._colors
        elif self.color_seps is not None:
            return get_colors_for_color_separators(self.color_seps)
        else:
            return [AVP(None, DEFAULT_COLOR)] * len(self.x_coords)

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
    def all_attributes(self):
        # FIXME where are these properties used? steamline them! include color seps?
        return chain(self.x_coords, self.y_coords, self.x_seps, self.y_seps, self.additional_data)

    def find_attributes(self, attribute: Attribute) -> List[AVP]:
        return [avp for avp in self.all_attributes if avp.attr == attribute]

    def variations_of(self, attribute: Attribute) -> List[Any]:
        relevant_values = [avp.val for avp in self.find_attributes(attribute)]
        return set(relevant_values)

    def would_be_in_same_plot(self, other: 'PlotInfo') -> bool:
        return self.x_seps == other.x_seps and self.y_seps == other.y_seps

    def get_viz_data(self, config) -> Tuple[str, str, str, str, Dict[str, List[Union[str, int, float]]]]:
        x_colname = self.x_coords[0].attr.col_name
        y_colname = self.y_coords[0].attr.col_name
        color_colname = '_color'
        size_colname = '_size'
        # DATA
        data = {
            x_colname: [avp.val for avp in self.x_coords],
            y_colname: [avp.val for avp in self.y_coords],
            color_colname: [avp.val for avp in self.colors],
            size_colname: [config.get_glyph_size(avp.val) for avp in self.sizes]
        }
        return x_colname, y_colname, color_colname, size_colname, data

    def __str__(self):
        return f'<{[x.val for x in self.x_coords]}:{[x.val for x in self.y_coords]}>(seps_x:{self.x_seps}, seps_y:{self.y_seps})'

    def __repr__(self):
        return str(self)
