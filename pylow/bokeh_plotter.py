
import pathlib
from itertools import chain
from typing import List, Tuple

from bokeh.io import output_notebook, show
from bokeh.models import (BasicTicker, CategoricalAxis, CategoricalTicker,
                          ColumnDataSource, DataRange1d, FactorRange, Grid,
                          HoverTool, Line, LinearAxis, Plot, Range1d,
                          SingleIntervalTicker)
from bokeh.models.glyphs import Circle, Text
from bokeh.sampledata.sprint import sprint


class BokehPlotter:

    def __init__(self, datasource, config):
        self.datasource = datasource
        self.config = config

    def create_viz(self):

        column = self.config.column_dimensions[0]
        measure = self.config.row_measures[0]
        data, labels = self.get_data()
        source = ColumnDataSource(data=data)
        print('Data is', data)
        x_range = FactorRange(*labels)

        measure_data = data[measure.col_name]
        _min, _max = min(measure_data), max(measure_data)
        _extra_range = (_max - _min) * 0.2
        y_range = Range1d(_min - _extra_range, _max + _extra_range)

        options = {'plot_width': 800, 'plot_height': 480, 'toolbar_location': None, 'outline_line_color': None}
        self.plot = Plot(x_range=x_range, y_range=y_range, **options)

        radius = dict(value=5, units='screen')
        glyph = Circle(x=column.col_name, y=measure.col_name, radius=radius)
        # glyph = Line(x='Category', y='Quantity')

        renderer = self.plot.add_glyph(source, glyph)

        # x-axis
        yticker = BasicTicker(num_minor_ticks=0)
        yaxis = LinearAxis(ticker=yticker, axis_label=measure.col_name)
        self.plot.add_layout(yaxis, 'right')
        ygrid = Grid(dimension=0, ticker=yaxis.ticker, grid_line_dash='dashed')
        self.plot.add_layout(ygrid)

        xticker = CategoricalTicker(name=column.col_name)
        xaxis = CategoricalAxis(ticker=xticker, axis_label=column.col_name, major_tick_in=-5, major_tick_out=10)
        self.plot.add_layout(xaxis, 'below')

        self.add_tooltips(renderer)

    def get_data(self) -> Tuple[ColumnDataSource, List[str]]:
        measure = self.config.row_measures[0]  # TODO iterate
        dimensions = [c.col_name for c in self.config.column_dimensions]
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
        columns = '\n'.join(column_template.format(d.col_name) for d in self.config.column_dimensions)
        # double-braces to escape the brace character, around another brace to encapsule columns with spaces
        measure_template = '<span style="font-size: 15px;">@{{{}}}</span>&nbsp;'
        measures = '\n'.join(measure_template.format(m.col_name) for m in self.config.row_measures)
        infos = measures + '<br>' + columns
        tooltip = f'<div>{infos}<div>'

        hover = HoverTool(tooltips=tooltip, renderers=[renderer])
        self.plot.add_tools(hover)

    def display(self, *, export_file=None, wait=False):
        show(self.plot)
