
import pathlib
from collections import defaultdict
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

from .plot_config import Attribute, Dimension, Measure
from .utils import make_unique_string_list

class BokehPlotter:

    def __init__(self, datasource, config):
        self.datasource = datasource
        self.config = config
        self.plots = []

    def get_values_from(self, attribute):
        return set(self.datasource.data[attribute.col_name])

    def get_column_amounts(self):
        x_lengths = [len(self.get_values_from(dim)) for dim in self.config.column_dimensions]
        x_length = reduce(lambda x, y: x * y, x_lengths)
        return x_length



    def create_viz(self):
        data = list(self.datasource.get_prepared_data(self.config.dimensions, self.config.measures))
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
            amount = ( 0 if i == 0 else 2) + 1  # FIXME must depend on previous amounts :/
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

        print('plots:', len(self.plots))
        # x_length = len(list(chain(*[self.get_values_from(dim) for dim in self.config.column_dimensions])))
        grid = gridplot(self.plots, ncols=1)
        show(grid)
