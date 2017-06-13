from itertools import chain
from typing import Dict, List, Tuple, Any, Union

from pylow.data.attributes import Attribute
from .avp import AVP
from .colorizer import DEFAULT_COLOR, get_colors_for_color_separators


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
    def colors(self) -> List[AVP]:
        if self._colors is not None:
            return self._colors
        elif self.color_seps is not None:
            return list(get_colors_for_color_separators(self.color_seps))
        else:
            return [AVP(None, DEFAULT_COLOR)] * len(self.x_coords)

    @colors.setter
    def colors(self, val) -> None:
        assert val is None or len(val) == len(self.x_coords)
        self._colors = val

    @property
    def sizes(self) -> List[AVP]:
        return self._sizes if self._sizes is not None else [AVP(None, 1)] * len(self.x_coords)

    @sizes.setter
    def sizes(self, val) -> None:
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
        return list(set(relevant_values))

    def would_be_in_same_plot(self, other: 'PlotInfo') -> bool:
        return self.x_seps == other.x_seps and self.y_seps == other.y_seps

    def get_viz_data(self, config) -> Tuple[str, str, str, str, Dict[str, List[Union[str, int, float]]]]:
        """ FIXME this is a bad return type

        :param config:
        :return:
        """
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
        xvals = [x.val for x in self.x_coords]
        yvals = [x.val for x in self.y_coords]
        return f'<{xvals}:{yvals}>(seps_x:{self.x_seps}, seps_y:{self.y_seps})'

    def __repr__(self):
        return str(self)
