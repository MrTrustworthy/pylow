from collections import defaultdict
from itertools import chain
from typing import Dict, List, Tuple, Union

from numpy import number
from pandas.core.groupby import DataFrameGroupBy

from data_preparation.plotinfo import PlotInfo
from pylow.data.attributes import Measure
from pylow.data.datasource import Datasource
from pylow.data.vizconfig import VizConfig
from pylow.data_preparation.avp import AVP
from pylow.data_preparation.plotinfobuilder import PlotInfoBuilder

Number = Union[int, float]


class Aggregator:
    """ The aggregator is the main object responsible for preparing the data for a visualization.

    It's the main interface for Plotters and, based on the VizConfig, compiles the raw data into a format
    that is useable by the Plotters (PlotInfo objects). It also maintains state information about the
    plots that is relevant for laying out the plot (number of columns and rows, min/max values, etc)
    """
    def __init__(self, datasource: Datasource, config: VizConfig):
        self.datasource = datasource
        self.config = config

        self.data = None  # type: List['PlotInfo']
        self.ncols, self.nrows, self.x_min, self.x_max, self.y_min, self.y_max = (0, 0, 0, 0, 0, 0)

    def is_in_first_column(self, plot_info: 'PlotInfo') -> bool:
        return self.data.index(plot_info) % self.ncols == 0

    def is_in_first_row(self, plot_info: 'PlotInfo') -> bool:
        return self.data.index(plot_info) < self.ncols

    def is_in_last_row(self, plot_info: 'PlotInfo') -> bool:
        return self.data.index(plot_info) >= len(self.data) - self.ncols

    def is_in_center_top_column(self, plot_info: 'PlotInfo') -> bool:
        return self.data.index(plot_info) == (self.ncols - 1) // 2

    def update_data(self) -> None:
        """ Main interface. Will update all the data of self.data based on the config and datasource
        """
        # TODO: Trigger refresh here once implementing observer pattern for vizconfigs

        raw_data = self._get_prepared_data()
        prepared = self._get_assigned_data(raw_data)
        final_data = PlotInfoBuilder.create_all_plotinfos(prepared, self.config)
        self._update_data_attributes(final_data)
        self.data = final_data

    # get meta-info
    def _update_data_attributes(self, data: List['PlotInfo']) -> None:
        """ Updates meta information about the data, such as:

        Amount of columns and rows and min/max values (including buffer for displaying) for X and Y axes
        """
        self.ncols = self._calculate_ncols(data)
        self.nrows = len(data) // self.ncols
        self._update_min_max_values(data, 'x')
        self._update_min_max_values(data, 'y')

    def _update_min_max_values(self, data: List['PlotInfo'], axis: str) -> None:
        # calculate min and max x_values
        _min_attr, _max_attr = f'{axis}_min', f'{axis}_max'
        vals = [avp.val for pi in data for avp in getattr(pi, f'{axis}_coords')]
        if len(vals) == 0:
            # This happens when there are no x_coords, such as for 0d0m_.... configurations
            setattr(self, _min_attr, None)
            setattr(self, _max_attr, None)
        else:
            setattr(self, _min_attr, min(vals))
            setattr(self, _max_attr, max(vals))

        # add some buffer for number varlues so the drawing looks better
        if isinstance(getattr(self, _min_attr), number):
            curr_min, curr_max = getattr(self, _min_attr), getattr(self, _max_attr)
            _range = int((curr_min - curr_max) / 10)
            setattr(self, _min_attr, curr_min - _range)
            setattr(self, _max_attr, curr_max + _range)

            # handle cases where there is only one measure and ranges don't make sense
            if getattr(self, _min_attr) == getattr(self, _max_attr):
                setattr(self, _min_attr, 0)
                # since the previous range difference & buffer is 0, add some buffer again
                setattr(self, _max_attr, curr_max + (curr_max * 0.1))

    def _calculate_ncols(self, data: List['PlotInfo']) -> int:
        column_possibilities = []
        for avp in data[0].x_seps:
            possibilities = len(self.datasource.get_variations_of(avp.attr))
            column_possibilities.append(possibilities)
        ncols = sum(column_possibilities)
        return max(ncols, 1)

    # prepare data
    def _get_assigned_data(self, data: Dict[Tuple[str], Tuple[Number]]) -> List[List[AVP]]:
        out = []
        for key_tuple, val_list in data.items():
            vals = [AVP(a, v) for a, v in zip(self.config.all_attrs, chain(key_tuple, val_list))]
            out.append(vals)
        return out

    def _get_prepared_data(self) -> Dict[Tuple[str], Tuple[Number]]:
        """ Returns a filtered and aggregated view on the data"""
        dimensions, measures = self.config.dimensions, self.config.measures
        grouped_data = self.datasource.group_by(dimensions)
        out = defaultdict(list)  # using defaultdict allows us to just append any measure to the end
        for measure in measures:
            aggregated_data = self._get_measure_data(grouped_data, measure)
            for key_tuple, value in aggregated_data.items():
                # for 0d0m-configurations, key_tuple may be a string instead of a tuple -> normalize to tuple
                if isinstance(key_tuple, str):
                    key_tuple = (key_tuple,)
                # for 0-Dimension-total configurations, key_tuple may be a bool (thats how panda does it)
                # FIXME not working currently - need to find a way to deal with a missing
                # FIXME y- or x-coord on a higher level and adapt here to reflect this
                if isinstance(key_tuple, bool):
                    key_tuple = tuple()
                out[key_tuple].append(value)
        return out

    def _get_measure_data(self, data: DataFrameGroupBy, measure: Measure) -> Dict[Tuple[str], int]:
        """ Helper for _get_prepared_data()"""
        # TODO: is the return type maybe Dict[Union[Tuple[str], str, bool], int] ?? bool in case of no aggregation
        grouped_measure = data[measure.col_name]
        aggregated_data = getattr(grouped_measure, measure.aggregation)()  # is a pandas object
        return aggregated_data.to_dict()
