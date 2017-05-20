
import pathlib
from itertools import chain
from typing import List, Tuple, Dict, Union

from bokeh.io import output_notebook, show
from bokeh.models import (BasicTicker, CategoricalAxis, CategoricalTicker,
                          ColumnDataSource, DataRange1d, FactorRange, Grid,
                          HoverTool, Line, LinearAxis, Plot, Range1d,
                          SingleIntervalTicker)
from bokeh.models.glyphs import Circle, Text
from bokeh.sampledata.sprint import sprint
from . import Attribute, Measure, Dimension

class BokehPlotter:

    def __init__(self, datasource, config):
        self.datasource = datasource
        self.config = config

    def create_viz(self):

        dimension = self.config.dimensions[0]
        measure = self.config.measures[0]

        data, labels = self.get_data(measure)
        source = ColumnDataSource(data=data)

        print('data', data, '\n', 'labels', labels)

        x_r, y_r = self.get_dimension_range(data, dimension), self.get_measure_range(data, measure)
        if measure in self.config.columns:
            x_r, y_r = y_r, x_r

        options = {'plot_width': 800, 'plot_height': 480, 'toolbar_location': None, 'outline_line_color': None}
        self.plot = Plot(x_range=x_r, y_range=y_r, **options)

        for attribute in (dimension, measure):
            self.draw_axes(attribute)

        x_n, y_n = dimension.col_name, measure.col_name
        if measure in self.config.columns:
            x_n, y_n = y_n, x_n
        radius = dict(value=5, units='screen')
        glyph = Circle(x=x_n, y=y_n, radius=radius)
        # glyph = Line(x='Category', y='Quantity')

        renderer = self.plot.add_glyph(source, glyph)

        self.add_tooltips(renderer)

    def get_dimension_range(self, data, dimension):
        return FactorRange(*data[dimension.col_name])

    def get_measure_range(self, data, measure, *, buffer=0.2):
        measure_data = data[measure.col_name]
        _min, _max = min(measure_data), max(measure_data)
        _extra_range = (_max - _min) * buffer
        range = Range1d(_min - _extra_range, _max + _extra_range)
        return range



    def draw_axes(self, attribute):
        orientation = 'below' if attribute in self.config.columns else 'left'
        self.draw_axis(attribute, orientation)

    def draw_axis(self, object: Attribute, position: str):

        ticker = BasicTicker(num_minor_ticks=0) if isinstance(object, Measure) else CategoricalTicker()
        options = {'ticker': ticker, 'axis_label': object.col_name}
        axis_constructor = LinearAxis if isinstance(object, Measure) else CategoricalAxis
        axis = axis_constructor(**options)
        self.plot.add_layout(axis, position)
        # ygrid = Grid(dimension=0, ticker=yaxis.ticker, grid_line_dash='dashed')
        # self.plot.add_layout(ygrid)


    def get_data(self, measure) -> Dict[str, List[Union[str, int, float]]]:
        dimensions = [c.col_name for c in self.config.dimensions]
        grouped_data = self.datasource.data.groupby(dimensions)
        grouped_measure = grouped_data[measure.col_name]
        aggregated_data = getattr(grouped_measure, measure.aggregation)().to_dict()  # is a pandas object
        factor_keys = list(aggregated_data.keys())

        prepared_data = {
            measure.col_name: list(aggregated_data.values()),
        }

        for i, dimension in enumerate(dimensions):
            dim_vals = list(aggregated_data.keys())  # Type: Union[Tuple[str], str]
            values = [t[i] for t in dim_vals] if isinstance(dim_vals[0], tuple) else dim_vals
            prepared_data[dimension] = values

        return prepared_data, factor_keys

    def add_tooltips(self, renderer):

        column_template = '<span style="font-size: 10px; color: #666;">(@{{{}}})</span>'
        columns = '\n'.join(column_template.format(d.col_name) for d in self.config.dimensions)
        # double-braces to escape the brace character, around another brace to encapsule columns with spaces
        measure_template = '<span style="font-size: 15px;">@{{{}}}</span>&nbsp;'
        measures = '\n'.join(measure_template.format(m.col_name) for m in self.config.measures)
        infos = measures + '<br>' + columns
        tooltip = f'<div>{infos}<div>'

        hover = HoverTool(tooltips=tooltip, renderers=[renderer])
        self.plot.add_tools(hover)

    def display(self, *, export_file=None, wait=False):
        show(self.plot)
