
import pathlib
from collections import defaultdict, namedtuple
from functools import reduce
from itertools import chain
from typing import Dict, Generator, List, Tuple, Union

from bokeh.io import output_notebook, show
from bokeh.layouts import gridplot
from bokeh.models import (BasicTicker, CategoricalAxis, CategoricalTicker,
                          ColumnDataSource, DataRange1d, FactorRange, Grid,
                          HoverTool, Line, LinearAxis, Plot, Range1d,
                          SingleIntervalTicker)
from bokeh.models.glyphs import Circle, Text
from bokeh.sampledata.sprint import sprint

from .datasource import Datasource
from .plot_config import Attribute, Dimension, Measure, VizConfig
from .utils import make_unique_string_list

# attribute_value pair
AVP = namedtuple('AVP', ['attr', 'val'])


class PlotInfo:

    def __init__(self,
                 x_coords: AVP = None,
                 y_coords: AVP = None,
                 x_seps: List[AVP] = None,
                 y_seps: List[AVP] = None
                 ):
        self.x_coords = x_coords
        self.y_coords = y_coords
        self.x_seps = x_seps
        self.y_seps = y_seps

    def __str__(self):
        return f'[{self.x_coords.val}:{self.y_coords.val}] (seps_x:{self.x_seps}, seps_y:{self.y_seps})'

    def __repr__(self):
        return str(self)

class Aggregator:

    def __init__(self, datasource: Datasource, config: VizConfig):
        self.datasource = datasource
        self.config = config
        self.all_attrs = list(chain(self.config.dimensions, self.config.measures))

        self.previous_columns = self.config.columns[:-1]
        self.last_column = self.config.columns[-1]

        self.previous_rows = self.config.rows[:-1]
        self.last_row = self.config.rows[-1]

    def get_data(self) -> List[PlotInfo]:
        data = self.get_prepared_data()
        prepared = self.get_assigned_data(data)
        out = [self.make_plot_info(d) for d in prepared]
        return out

    def make_plot_info(self, plot_data: List[AVP]) -> PlotInfo:

        x_coords = plot_data[self.all_attrs.index(self.last_column)]
        y_coords = plot_data[self.all_attrs.index(self.last_row)]
        x_seps = [plot_data[self.all_attrs.index(col)] for col in self.previous_columns]
        y_seps = [plot_data[self.all_attrs.index(col)] for col in self.previous_rows]
        plotinfo = PlotInfo(x_coords, y_coords, x_seps, y_seps)
        return plotinfo

    def get_assigned_data(self, data) -> List[List[AVP]]:
        out = []
        for key_tuple, val_list in data.items():
            vals = [AVP(a, v) for a, v in zip(self.all_attrs, chain(key_tuple, val_list))]
            out.append(vals)
        return out

    def get_prepared_data(self) -> Dict[Tuple[str], Tuple[int]]:
        dimensions, measures = self.config.dimensions, self.config.measures
        dimension_names = [d.col_name for d in dimensions]
        grouped_data = self.datasource.data.groupby(dimension_names)
        out = {}
        for measure in measures:
            aggregated_data = self.get_measure_data(grouped_data, measure)
            for key_tuple, value in aggregated_data.items():
                if not key_tuple in out:
                    out[key_tuple] = [value]
                else:
                    out[key_tuple].append(value)
        return out

    def get_measure_data(self, data, measure) -> Dict[Tuple[str], int]:
        grouped_measure = data[measure.col_name]
        aggregated_data = getattr(grouped_measure, measure.aggregation)()  # is a pandas object
        return aggregated_data.to_dict()


class BokehPlotter:

    def __init__(self, datasource, config):
        self.datasource = datasource
        self.config = config
        self.plots = []

    def create_viz(self):
        aggregator = Aggregator(self.datasource, self.config)
        data = aggregator.get_data()
        # TODO create VIZ_INFO object from that data
        print('data', data)

        return

        measure, dataset = data[0]

        for row_tuple, column_data in self.get_column_data(dataset).items():
            plot = self.make_column_plot(row_tuple, column_data)
            self.plots.append(plot)

    def get_column_data(self, data) -> Dict[Tuple[str], List[Tuple[Tuple[str], int]]]:
        col_amount = len(self.config.column_dimensions)

        out = defaultdict(list)

        for key_tuple, value in data.items():
            col_tuple, row_tuple = key_tuple[:col_amount], key_tuple[col_amount:]
            out[row_tuple].append((col_tuple, value))
        return out

    def make_column_plot(self, row_tuple: Tuple[str], column_data: List[Tuple[Tuple[str], int]]):

        data = {
            'key': ['/'.join(t[0]) for t in column_data],
            'val': [t[1] for t in column_data]
        }

        source = ColumnDataSource(data=data)
        # ranges
        x_r, y_r = FactorRange(*data['key']), Range1d(min(data['val']), max(data['val']))
        options = {'plot_width': 1000, 'plot_height': 500, 'toolbar_location': None, 'outline_line_color': '#00FF00'}
        plot = Plot(x_range=x_r, y_range=y_r, **options)

        extra_data = {}
        for i in range(len(column_data[0][0])):
            amount = (0 if i == 0 else 2) + 1  # FIXME must depend on previous amounts :/
            unique_values = list(set([t[0][i] for t in column_data]))
            labels_to_show = make_unique_string_list(unique_values * amount)
            extra_data['key_label_' + str(i)] = FactorRange(*labels_to_show)

        plot.extra_x_ranges = extra_data

        radius = dict(value=5, units='screen')
        glyph = Circle(x='key', y='val', radius=radius)
        renderer = plot.add_glyph(source, glyph)
        self.add_axes(plot, column_data)
        return plot

    def add_axes(self, plot, data):
        dimension_amount = len(data[0][0])
        reverse_indicies = list(range(dimension_amount))[::-1]
        for i, orientation in zip(reverse_indicies, ('below', 'above', 'above', 'above')):
            x_ticker = CategoricalTicker()
            x_axis = CategoricalAxis(ticker=x_ticker, axis_label=str(i), x_range_name='key_label_' + str(i))
            plot.add_layout(x_axis, orientation)

        y_ticker = BasicTicker(num_minor_ticks=0)
        y_axis = LinearAxis(ticker=y_ticker, axis_label='val')
        plot.add_layout(y_axis, 'left')

    def display(self, *, export_file=None, wait=False):
        return
        print('plots:', len(self.plots))
        # x_length = len(list(chain(*[self.get_values_from(dim) for dim in self.config.column_dimensions])))
        grid = gridplot(self.plots, ncols=1)
        show(grid)
