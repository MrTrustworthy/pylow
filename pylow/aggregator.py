from functools import reduce
from itertools import chain
from typing import Dict, List, Tuple

from .datasource import Datasource
from .plot_config import Attribute, Dimension, Measure, VizConfig
from .plotinfo import AVP, PlotInfo


class Aggregator:

    def __init__(self, datasource: Datasource, config: VizConfig):
        self.datasource = datasource
        self.config = config

        self.data = None  # is set by update_data

        self.all_attrs = list(chain(self.config.dimensions, self.config.measures))

        self.previous_columns = self.config.columns[:-1]
        self.last_column = self.config.columns[-1]

        self.previous_rows = self.config.rows[:-1]
        self.last_row = self.config.rows[-1]

        self.ncols, self.nrows, self.x_min, self.x_max, self.y_min, self.y_max = (0, 0, 0, 0, 0, 0)

    def update_data(self) -> List[PlotInfo]:
        data = self._get_prepared_data()
        prepared = self._get_assigned_data(data)
        out = list(set(self._make_plot_info(d) for d in prepared))  # may yield duplicates
        self.data = out
        PlotInfo.clear_point_cache()
        self._update_data_attributes()

    def _update_data_attributes(self):
        self.ncols = self._calculate_ncols()
        self.nrows = len(self.data) / self.ncols
        x_vals = [avp.val for pi in self.data for avp in pi.x_coords]
        self.x_min, self.x_max = min(x_vals), max(x_vals)
        y_vals = [avp.val for pi in self.data for avp in pi.y_coords]
        self.y_min, self.y_max = min(y_vals), max(y_vals)

    def _calculate_ncols(self):
        column_possibilities = []
        for avp in self.data[0].x_seps:
            possibilities = len(self.datasource.get_variations_of(avp.attr))
            column_possibilities.append(possibilities)
        ncols = reduce(lambda x, y: x + y, column_possibilities)
        return ncols

    def _make_plot_info(self, plot_data: List[AVP]) -> PlotInfo:

        x_coords = [plot_data[self.all_attrs.index(self.last_column)]]
        y_coords = [plot_data[self.all_attrs.index(self.last_row)]]
        x_seps = [plot_data[self.all_attrs.index(col)] for col in self.previous_columns]
        y_seps = [plot_data[self.all_attrs.index(col)] for col in self.previous_rows]
        plotinfo = PlotInfo.create_new_or_update(x_coords, y_coords, x_seps, y_seps)
        return plotinfo

    def _get_assigned_data(self, data) -> List[List[AVP]]:
        out = []
        for key_tuple, val_list in data.items():
            vals = [AVP(a, v) for a, v in zip(self.all_attrs, chain(key_tuple, val_list))]
            out.append(vals)
        return out

    def _get_prepared_data(self) -> Dict[Tuple[str], Tuple[int]]:
        dimensions, measures = self.config.dimensions, self.config.measures
        dimension_names = [d.col_name for d in dimensions]
        grouped_data = self.datasource.data.groupby(dimension_names)
        out = {}
        for measure in measures:
            aggregated_data = self._get_measure_data(grouped_data, measure)
            for key_tuple, value in aggregated_data.items():
                if not key_tuple in out:
                    out[key_tuple] = [value]
                else:
                    out[key_tuple].append(value)
        return out

    def _get_measure_data(self, data, measure) -> Dict[Tuple[str], int]:
        grouped_measure = data[measure.col_name]
        aggregated_data = getattr(grouped_measure, measure.aggregation)()  # is a pandas object
        return aggregated_data.to_dict()
