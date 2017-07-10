from itertools import chain
from typing import Dict, List, Any

from pylow.data.attributes import Attribute
from pylow.data_preparation.avp import AVP
from pylow.data_preparation.colorization_behaviour import ColorizationBehaviour
from pylow.data_preparation.sizing_behaviour import SizingBehaviour
from pylow.utils import ColumnNameCollection

DEFAULT_AVP = AVP(Attribute(''), '')


class PlotInfo:
    def __init__(
            self,
            x_coords: List[AVP],
            y_coords: List[AVP],
            x_seps: List[AVP],
            y_seps: List[AVP],
            additional_data: List[AVP],
            colorization_behaviour: ColorizationBehaviour,
            sizing_behaviour: SizingBehaviour
    ) -> None:
        # those two should be the same, or at least one is non-existent
        assert len(x_coords) == len(y_coords) or min(len(x_coords), len(y_coords)) == 0

        self.x_coords = x_coords
        self.y_coords = y_coords
        self.x_seps = x_seps
        self.y_seps = y_seps
        self.additional_data = additional_data
        self.colorization_behaviour = colorization_behaviour
        self.sizing_behaviour = sizing_behaviour

    @property
    def colors(self) -> List[AVP]:
        return self.colorization_behaviour.get_colors(self)

    @property
    def sizes(self) -> List[AVP]:
        return self.sizing_behaviour.get_sizes(self)

    @property
    def column_names(self) -> ColumnNameCollection:
        """ Returns a namedtuple that contains all column names for this data (x, y, size, color)

        This is needed at plotting to match column names to data and to provide labels for the axes etc.
        """
        x_colname = self.get_example_avp_for_axis('x').attr.col_name
        y_colname = self.get_example_avp_for_axis('y').attr.col_name
        color_colname = '_color'
        size_colname = '_size'

        col_names = ColumnNameCollection(x_colname, y_colname, color_colname, size_colname)
        return col_names

    def find_attributes(self, attribute: Attribute) -> List[AVP]:
        all_attributes = chain(self.x_coords, self.y_coords, self.x_seps, self.y_seps, self.additional_data)
        return [avp for avp in all_attributes if avp.attr == attribute]

    def variations_of(self, attribute: Attribute) -> List[Any]:
        relevant_values = [avp.val for avp in self.find_attributes(attribute)]
        return list(set(relevant_values))

    def is_in_plot_of(self, other_x_seps: List[AVP], other_y_seps: List[AVP]) -> bool:
        return self.x_seps == other_x_seps and self.y_seps == other_y_seps

    def get_axis_label(self, x_or_y: str) -> str:
        """ Returns the 'last' x or y dimension value this plot is split by"""
        # FIXME inserting \n does nothing, display output is wrong, see Issue #2
        attrs = getattr(self, f'{x_or_y}_seps')
        if len(attrs) == 0:
            return ''
        else:
            return attrs[-1].val

    def get_coord_values(self, x_or_y: str) -> List[Any]:
        """ Will return all values for a given coords axis
        If the axis is empty, will return a default AVP
        """
        other = 'y' if x_or_y is 'x' else 'x'
        vals = getattr(self, f'{x_or_y}_coords')
        if len(vals) > 0:
            return [avp.val for avp in vals]
        else:
            return [DEFAULT_AVP.val] * len(self.get_coord_values(other))

    def get_example_avp_for_axis(self, x_or_y: str) -> AVP:
        """Returns an example AVP for the x- or y_coords

        Originates from issue #25
        """

        values = getattr(self, f'{x_or_y}_coords')
        if len(values) > 0:
            return values[0]
        return DEFAULT_AVP

    def get_viz_data(self) -> Dict[str, List[Any]]:
        """ Returns the data that is supposed to be drawn in a fitting format
        """
        x, y, color, size = self.column_names
        data = {
            x: self.get_coord_values('x'),  # default value for 0d0m_xd1m configs
            y: self.get_coord_values('y'),  # default value for xd1m_0d0m configs
            color: [avp.val for avp in self.colors],
            size: [avp.val for avp in self.sizes]
        }
        return data

    def __repr__(self):
        xvals = [x.val for x in self.x_coords]
        yvals = [x.val for x in self.y_coords]
        col_b = self.colorization_behaviour
        size_b = self.sizing_behaviour
        return f'<PlotInfo: [{xvals}|{yvals}] [[{self.x_seps}||{self.y_seps}]] ({repr(col_b)}|{repr(size_b)})'
