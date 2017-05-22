
import pathlib
from itertools import chain
from typing import Dict, List, Tuple, Union, Generator
from collections import defaultdict

from bokeh.io import output_notebook, show
from bokeh.layouts import gridplot
from bokeh.models import (BasicTicker, CategoricalAxis, CategoricalTicker,
                          ColumnDataSource, DataRange1d, FactorRange, Grid,
                          HoverTool, Line, LinearAxis, Plot, Range1d,
                          SingleIntervalTicker)
from bokeh.models.glyphs import Circle, Text
from bokeh.sampledata.sprint import sprint
from functools import reduce
from . import Attribute, Dimension, Measure


class BokehPlotter:

    def __init__(self, datasource, config):
        self.datasource = datasource
        self.config = config
        self.plots = []

    def get_values_from(self, attribute):
        return set(self.datasource.data[attribute.col_name])

    def get_column_amounts(self):
        x_lengths = [len(self.get_values_from(dim)) for dim in self.config.column_dimensions]
        x_length = reduce(lambda x, y: x*y, x_lengths)
        return x_length

    def create_viz(self):
        data = list(self.get_data())
        measure, dataset = data[0]

        for row_tuple, column_data in self.get_column_data(dataset).items():
            plot = self.make_column_plot(row_tuple, column_data)
            self.plots.append(plot)

        # for key_tuple, value in dataset.items():
        #     plot = self.make_plot(key_tuple, value)
        #     self.plots.append(plot)

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
            extra_data['key_label_' + str(i)] = FactorRange(*[t[0][i] for t in column_data])

        plot.extra_x_ranges = extra_data

        radius = dict(value=5, units='screen')
        glyph = Circle(x='key', y='val', radius=radius)
        renderer = plot.add_glyph(source, glyph)
        self.add_axes(plot, column_data)
        return plot

    def add_axes(self, plot, data):

        for i, orientation in zip(range(len(data[0][0])), ('below', 'above')):
            x_ticker = CategoricalTicker()
            x_axis = CategoricalAxis(ticker=x_ticker, axis_label=str(i), x_range_name='key_label_' + str(i))
            plot.add_layout(x_axis, 'below')


        y_ticker = BasicTicker(num_minor_ticks=0)
        y_axis = LinearAxis(ticker=y_ticker, axis_label='val')
        plot.add_layout(y_axis, 'left')

    def get_data(self) -> Generator[Tuple[Measure, 'pandas.Series'], None, None]:
        dimensions = [d.col_name for d in self.config.dimensions]
        grouped_data = self.datasource.data.groupby(dimensions)
        for measure in self.config.measures:
            grouped_measure = grouped_data[measure.col_name]
            aggregated_data = getattr(grouped_measure, measure.aggregation)().to_dict()  # is a pandas object
            yield measure, aggregated_data


    def display(self, *, export_file=None, wait=False):

        print('plots:', len(self.plots))
        # x_length = len(list(chain(*[self.get_values_from(dim) for dim in self.config.column_dimensions])))
        grid = gridplot(self.plots, ncols=1)
        show(grid)
