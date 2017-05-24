
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
from .plotinfo import AVP, PlotInfo
from .aggregator import Aggregator
from .utils import make_unique_string_list


class BokehPlotter:

    def __init__(self, datasource, config):
        self.aggregator = Aggregator(datasource, config)
        self.plots = []

    def create_viz(self):
        self.aggregator.update_data()
        data = self.aggregator.data

        for plotinfo in data:
            plot = self.make_plot(plotinfo)
            self.plots.append(plot)

    def make_plot(self, plot_info: PlotInfo):

        x_colname = plot_info.x_coords[0].attr.col_name
        y_colname = plot_info.y_coords[0].attr.col_name
        data = {
            x_colname: [avp.val for avp in plot_info.x_coords],
            y_colname: [avp.val for avp in plot_info.y_coords],
        }

        source = ColumnDataSource(data=data)
        # ranges
        x_r, y_r = self.get_range(plot_info, 'x'), self.get_range(plot_info, 'y')

        options = {
            'plot_width': int(1200 / self.aggregator.ncols),
            'plot_height': int(800 / self.aggregator.nrows),
            'toolbar_location': None,
            'x_range': x_r,
            'y_range': y_r,
        }
        plot = Plot(**options)
        plot.title.text = plot_info.x_seps[-1].val  # also see title_location

        x_ax, y_ax = self.get_axis(plot_info, 'x'), self.get_axis(plot_info, 'y')
        plot.add_layout(x_ax, 'above')
        plot.add_layout(y_ax, 'left')

        radius = dict(value=5, units='screen')
        glyph = Circle(x=x_colname, y=y_colname, radius=radius)
        renderer = plot.add_glyph(source, glyph)
        # self.add_axes(plot, column_data)
        return plot

    def get_range(self, data: PlotInfo, axis: str):
        values = [avp.val for avp in getattr(data, f'{axis}_coords')]
        if isinstance(values[0], str):
            return FactorRange(*values)
        else:
            _min, _max = getattr(self.aggregator, f'{axis}_min'), getattr(self.aggregator, f'{axis}_max')
            return Range1d(_min, _max)

    def get_axis(self, data: PlotInfo, axis: str):
        values = [avp.val for avp in getattr(data, f'{axis}_coords')]
        label = [avp.attr for avp in getattr(data, f'{axis}_coords')][0].col_name
        if isinstance(values[0], str):
            ticker = CategoricalTicker()
            axis = CategoricalAxis(ticker=ticker, axis_label=label)
            return axis
        else:
            ticker = BasicTicker(num_minor_ticks=0)
            axis = LinearAxis(ticker=ticker, axis_label=label)
            return axis

    def display(self, *, export_file=None, wait=False):
        grid = gridplot(self.plots, ncols=self.aggregator.ncols)
        show(grid)
