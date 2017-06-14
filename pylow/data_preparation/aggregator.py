from functools import reduce
from itertools import chain
from typing import Any, Dict, List, Tuple, Union

from .avp import AVP
from .colorizer import ALL_COLORS, DEFAULT_COLOR, adjust_brightness
from numpy import number

from pylow.data.datasource import Datasource
from pylow.data.vizconfig import VizConfig
from pylow.data.attributes import Dimension, Measure
from pylow.data_preparation.plotinfo import PlotInfo
from pylow.data_preparation.plotinfobuilder import PlotInfoBuilder
from pylow.utils import reverse_lerp

Number = Union[int, float]


class Aggregator:

    def __init__(self, datasource: Datasource, config: VizConfig):
        self.datasource = datasource
        self.config = config

        self.data = None  # type: List[PlotInfo]
        self.ncols, self.nrows, self.x_min, self.x_max, self.y_min, self.y_max = (0, 0, 0, 0, 0, 0)

    def is_in_first_column(self, plot_info: PlotInfo) -> bool:
        return self.data.index(plot_info) % self.ncols == 0

    def is_in_first_row(self, plot_info: PlotInfo) -> bool:
        return self.data.index(plot_info) < self.ncols

    def is_in_last_row(self, plot_info: PlotInfo) -> bool:
        return self.data.index(plot_info) >= len(self.data) - self.ncols

    def is_in_center_top_column(self, plot_info: PlotInfo) -> bool:
        return self.data.index(plot_info) == (self.ncols - 1) // 2

    def update_data(self) -> None:

        raw_data = self._get_prepared_data()
        prepared = self._get_assigned_data(raw_data)

        final_data = PlotInfoBuilder.create_all_plotinfos(prepared, self.config)

        self._add_plot_info_sizes_and_colors(final_data)
        self._update_data_attributes(final_data)

        self.data = final_data

    # TODO FIXME Move to plotinfobuilder, this is so ugly here
    # sizes and colors
    def _add_plot_info_sizes_and_colors(self, data: List[PlotInfo]) -> None:
        for attr in ('size', 'color'):
            if getattr(self.config, attr) is not None:
                self._add_plot_info_sizes_and_colors_from_conf(data, attr)

    def _add_plot_info_sizes_and_colors_from_conf(self, data: List[PlotInfo], attr: str) -> None:
        # find all possible values that are in any plot of the screen
        config_attribute = getattr(self.config, attr)
        val_variation_lists = (plotinfo.variations_of(config_attribute) for plotinfo in data)
        val_variations = sorted(set(chain(*val_variation_lists)))

        for plot_info in data:
            # get the values of the size- or color-attribute of the current plotinfo
            # TODO FIXME: Find out how to handle cases where the attribute is not elsewhere on the plot
            attribute_vals = [avp.val for avp in plot_info.find_attributes(config_attribute)]
            # create a avp with (Attribute, float_of_size or hex_of_color) for each value
            getter_func = getattr(self, f'_get_{attr}_data')
            avps = [getter_func(curr_val, val_variations) for curr_val in attribute_vals]
            setattr(plot_info, f'{attr}s', avps)

    def _get_size_data(self, current_val: Any, possible_vals: List[Any]) -> AVP:
        if isinstance(self.config.size, Dimension):
            # TODO FIXME currently, size only affects plot in one direction -> bigger, need to clamp this
            size = possible_vals.index(current_val)
            size_avp = AVP(self.config.size, (size + 1))
            return size_avp
        else:  # for measures
            relative_in_range = reverse_lerp(current_val, possible_vals)  # between 0 and 1
            # turn into value from 0.5 to 2
            size_factor = (relative_in_range + 0.5) * (4/3)
            size_avp = AVP(self.config.size, size_factor)
            return size_avp

    def _get_color_data(self, current_val: Any, possible_vals: List[Any]) -> AVP:
        if isinstance(self.config.color, Dimension):
            color = ALL_COLORS[possible_vals.index(current_val)]
            color_avp = AVP(self.config.color, color)
            return color_avp
        else:  # for measures
            relative_in_range = reverse_lerp(current_val, possible_vals)  # between 0 and 1
            # turn into value from -0.5 and 0.5 with 0.5 for the smallest values
            color_saturation = (relative_in_range - 0.5) * -1
            color = adjust_brightness(DEFAULT_COLOR, color_saturation)
            color_avp = AVP(self.config.color, color)
            return color_avp

    # get meta-info
    def _update_data_attributes(self, data: List[PlotInfo]) -> None:
        self.ncols = self._calculate_ncols(data)
        self.nrows = len(data) // self.ncols
        x_vals = [avp.val for pi in data for avp in pi.x_coords]
        self.x_min, self.x_max = min(x_vals), max(x_vals)
        y_vals = [avp.val for pi in data for avp in pi.y_coords]
        self.y_min, self.y_max = min(y_vals), max(y_vals)

        # add some buffer so the drawing looks better
        if isinstance(self.y_min, number):
            range = int((self.y_max - self.y_min) / 10)
            self.y_min, self.y_max = self.y_min - range, self.y_max + range

        if isinstance(self.x_min, number):
            range = int((self.x_max - self.x_min) / 10)
            self.x_min, self.x_max = self.x_min - range, self.x_max + range

    def _calculate_ncols(self, data: List[PlotInfo]) -> int:
        column_possibilities = []
        for avp in data[0].x_seps:
            possibilities = len(self.datasource.get_variations_of(avp.attr))
            column_possibilities.append(possibilities)
        ncols = reduce(lambda x, y: x + y, column_possibilities)
        return ncols

    # prepare data
    def _get_assigned_data(self, data) -> List[List[AVP]]:
        out = []
        for key_tuple, val_list in data.items():
            vals = [AVP(a, v) for a, v in zip(self.config.all_attrs, chain(key_tuple, val_list))]
            out.append(vals)
        return out

    def _get_prepared_data(self) -> Dict[Tuple[str], Tuple[Number]]:
        dimensions, measures = self.config.dimensions, self.config.measures
        dimension_names = [d.col_name for d in dimensions]
        grouped_data = self.datasource.data.groupby(dimension_names)
        out = {}
        for measure in measures:
            aggregated_data = self._get_measure_data(grouped_data, measure)
            for key_tuple, value in aggregated_data.items():
                if key_tuple not in out:
                    out[key_tuple] = [value]
                else:
                    out[key_tuple].append(value)
        return out

    def _get_measure_data(self, data, measure: Measure) -> Dict[Tuple[str], int]:
        grouped_measure = data[measure.col_name]
        aggregated_data = getattr(grouped_measure, measure.aggregation)()  # is a pandas object
        return aggregated_data.to_dict()