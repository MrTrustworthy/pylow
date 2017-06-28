from itertools import chain
from typing import Dict, List, Tuple, Any, Union

from pylow.data.attributes import Attribute
from pylow.data_preparation.avp import AVP
from pylow.data_preparation.colorization_behaviour import ColorizationBehaviour
from pylow.data_preparation.sizing_behaviour import SizingBehaviour

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
    ):
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

    def find_attributes(self, attribute: Attribute) -> List[AVP]:
        all_attributes = chain(self.x_coords, self.y_coords, self.x_seps, self.y_seps, self.additional_data)
        return [avp for avp in all_attributes if avp.attr == attribute]

    def variations_of(self, attribute: Attribute) -> List[Any]:
        relevant_values = [avp.val for avp in self.find_attributes(attribute)]
        return list(set(relevant_values))

    def would_be_in_same_plot(self, other: 'PlotInfo') -> bool:
        return self.x_seps == other.x_seps and self.y_seps == other.y_seps

    def get_coord_values(self, x_or_y: str) -> List[Any]:
        """ Will return all values for a given coords axis
        If the axis is empty, will return a default AVP
        """

        vals = getattr(self, f'{x_or_y}_coords')
        if len(vals) > 0:
            return [avp.val for avp in vals]
        else:
            return [DEFAULT_AVP.val]

    def get_example_avp_for_axis(self, x_or_y: str) -> AVP:
        """Returns an example AVP for the x- or y_coords

        Originates from issue #25
        """

        values = getattr(self, f'{x_or_y}_coords')
        if len(values) > 0:
            return values[0]
        return DEFAULT_AVP


    def get_viz_data(self) -> Tuple[str, str, str, str, Dict[str, List[Union[str, int, float]]]]:
        # FIXME holy crap this method is atrocious, the return type makes my eyes water
        # FIXME FIXME FIXME

        x_colname = self.get_example_avp_for_axis('x').attr.col_name
        y_colname = self.get_example_avp_for_axis('y').attr.col_name
        color_colname = '_color'
        size_colname = '_size'
        # DATA
        data = {
            x_colname: self.get_coord_values('x'),  # default value for 0d0m_xd1m configs
            y_colname: self.get_coord_values('y'),  # default value for xd1m_0d0m configs
            color_colname: [avp.val for avp in self.colors],
            size_colname: [avp.val for avp in self.sizes]
        }
        return x_colname, y_colname, color_colname, size_colname, data

    def __str__(self):
        xvals = [x.val for x in self.x_coords]
        yvals = [x.val for x in self.y_coords]
        return f'<{xvals}:{yvals}>(seps_x:{self.x_seps}, seps_y:{self.y_seps})'

    def __repr__(self):
        return str(self)
