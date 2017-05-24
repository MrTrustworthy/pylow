from functools import reduce
from itertools import chain
from typing import Dict, List, Tuple

from numpy import number

from .datasource import Datasource
from .plot_config import Attribute, Dimension, Measure, VizConfig
from .plotinfo import AVP, PlotInfo


class Aggregator:

    def __init__(self, datasource: Datasource, config: VizConfig):
        self.datasource = datasource
        self.config = config

        self.data = None  # type: List[PlotInfo]

        self.all_attrs = list(chain(self.config.dimensions, self.config.measures))

        self.previous_columns = self.config.columns[:-1]
        self.last_column = self.config.columns[-1]

        self.previous_rows = self.config.rows[:-1]
        self.last_row = self.config.rows[-1]

        self.ncols, self.nrows, self.x_min, self.x_max, self.y_min, self.y_max = (0, 0, 0, 0, 0, 0)

    def update_data(self) -> None:
        data = self._get_prepared_data()
        prepared = self._get_assigned_data(data)
        out = list(set(self._make_plot_info(d) for d in prepared))  # may yield duplicates
        # sort data so that dimensions and measures stay grouped
        out.sort(key=lambda x: [avp.val for avp in chain(x.y_seps[::-1], x.x_seps[::-1])])
        self.data = out
        PlotInfo.clear_point_cache()
        self._update_data_attributes()

    def is_in_first_column(self, plot_info: PlotInfo) -> bool:
        return self.data.index(plot_info) % self.ncols == 0

    def is_in_first_row(self, plot_info: PlotInfo) -> bool:
        return self.data.index(plot_info) < self.ncols

    def is_in_last_row(self, plot_info: PlotInfo) -> bool:
        return self.data.index(plot_info) >= len(self.data) - self.ncols

    def _update_data_attributes(self):
        self.ncols = self._calculate_ncols()
        self.nrows = len(self.data) // self.ncols
        x_vals = [avp.val for pi in self.data for avp in pi.x_coords]
        self.x_min, self.x_max = min(x_vals), max(x_vals)
        y_vals = [avp.val for pi in self.data for avp in pi.y_coords]
        self.y_min, self.y_max = min(y_vals), max(y_vals)

        # add some buffer so the drawing looks better
        if isinstance(self.y_min, number):
            range = int((self.y_max - self.y_min) / 10)
            self.y_min, self.y_max = self.y_min - range, self.y_max + range

        if isinstance(self.x_min, number):
            range = int((self.x_max - self.x_min) / 10)
            self.x_min, self.x_max = self.x_min - range, self.x_max + range

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
