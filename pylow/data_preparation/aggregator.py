from collections import defaultdict
from itertools import chain
from typing import Dict, List, Tuple, Union

from numpy import number

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

        # calculate min and max x_values
        x_vals = [avp.val for pi in data for avp in pi.x_coords]
        if len(x_vals) == 0:
            # This happens when there are no x_coords, such as for 0d0m_.... configurations
            self.x_min, self.x_max = (None, None)
        else:
            self.x_min, self.x_max = min(x_vals), max(x_vals)

        # calculate min and max y_values
        y_vals = [avp.val for pi in data for avp in pi.y_coords]
        if len(y_vals) == 0:
            # This happens when there are no y_coords, such as for ...._0d0m configurations
            self.y_min, self.y_max = (None, None)
        else:
            self.y_min, self.y_max = min(y_vals), max(y_vals)

        # add some buffer so the drawing looks better
        if isinstance(self.y_min, number):
            _range = int((self.y_max - self.y_min) / 10)
            self.y_min, self.y_max = self.y_min - _range, self.y_max + _range

        if isinstance(self.x_min, number):
            _range = int((self.x_max - self.x_min) / 10)
            self.x_min, self.x_max = self.x_min - _range, self.x_max + _range

    def _calculate_ncols(self, data: List['PlotInfo']) -> int:
        column_possibilities = []
        for avp in data[0].x_seps:
            possibilities = len(self.datasource.get_variations_of(avp.attr))
            column_possibilities.append(possibilities)
        ncols = sum(column_possibilities)
        return max(ncols, 1)

    # prepare data
    def _get_assigned_data(self, data: Dict[Union[Tuple[str], str], List[Number]]) -> List[List[AVP]]:
        out = []
        for key_tuple, val_list in data.items():
            vals = [AVP(a, v) for a, v in zip(self.config.all_attrs, chain(key_tuple, val_list))]
            out.append(vals)
        return out

    def _get_prepared_data(self) -> Dict[Tuple[str], Tuple[Number]]:
        dimensions, measures = self.config.dimensions, self.config.measures
        dimension_names = [d.col_name for d in dimensions]
        grouped_data = self.datasource.data.groupby(dimension_names)
        out = defaultdict(list)  # using defaultdict allows us to just append any measure to the end
        for measure in measures:
            aggregated_data = self._get_measure_data(grouped_data, measure)
            for key_tuple, value in aggregated_data.items():
                # for 0d0m-configurations, key_tuple may be a string instead of a tuple -> normalize to tuple
                if isinstance(key_tuple, str):
                    key_tuple = (key_tuple,)
                out[key_tuple].append(value)
        return out

    def _get_measure_data(self, data, measure: Measure) -> Dict[Tuple[str], int]:
        grouped_measure = data[measure.col_name]
        aggregated_data = getattr(grouped_measure, measure.aggregation)()  # is a pandas object
        return aggregated_data.to_dict()
