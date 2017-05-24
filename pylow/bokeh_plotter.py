
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
from bokeh.models.glyphs import Circle, Text, VBar, Line, Text
from bokeh.sampledata.sprint import sprint
from bokeh.models.annotations import Title, Label

from .aggregator import Aggregator
from .datasource import Datasource
from .plot_config import Attribute, Dimension, Measure, VizConfig
from .plotinfo import AVP, PlotInfo
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

        # DATA
        data = {
            x_colname: [avp.val for avp in plot_info.x_coords],
            y_colname: [avp.val for avp in plot_info.y_coords],
        }
        source = ColumnDataSource(data=data)

        # RANGES
        x_r, y_r = self.get_range(plot_info, 'x'), self.get_range(plot_info, 'y')

        # PLOT
        options = {
            'plot_width': int(1200 / self.aggregator.ncols),
            'plot_height': int(800 / self.aggregator.nrows),
            'toolbar_location': None,
            'x_range': x_r,
            'y_range': y_r,
        }
        if self.aggregator.is_in_first_row(plot_info):
            # TODO multiple titles for multiple layers of dimensions
            options['title'] = Title(text=plot_info.x_seps[-1].val, align='center')

        plot = Plot(**options)

        # Labels on the left
        if self.aggregator.is_in_first_column(plot_info):
            label = Label(x=0, y=options['plot_height']//2, x_units='screen', y_units='screen', text=plot_info.y_seps[-1].val, render_mode='css', text_align='right')

            plot.add_layout(label)

        # AXES
        if self.aggregator.is_in_last_row(plot_info):
            x_ax = self.get_axis(plot_info, 'x')
            plot.add_layout(x_ax, 'below')

        if self.aggregator.is_in_first_column(plot_info):
            y_ax = self.get_axis(plot_info, 'y')
            plot.add_layout(y_ax, 'left')

        # GLYPH
        glyph = self.create_glyph(x_colname, y_colname)
        renderer = plot.add_glyph(source, glyph)

        # HOVER
        hover = self.get_tooltip(renderer, plot_info)
        plot.add_tools(hover)
        return plot

    def create_glyph(self, x_colname, y_colname):
        if 'some_condition':
            return Line(x=x_colname, y=y_colname, line_width=2)
        elif not 'some_condition':  # TODO FIXME
            return VBar(x=x_colname, top=y_colname)
        else:
            radius = dict(value=5, units='screen')
            return Circle(x=x_colname, y=y_colname, radius=radius)

    def get_range(self, data: PlotInfo, axis: str):
        values = [avp.val for avp in getattr(data, f'{axis}_coords')]
        if isinstance(values[0], str):
            return FactorRange(*values)
        else:
            _min, _max = getattr(self.aggregator, f'{axis}_min'), getattr(self.aggregator, f'{axis}_max')
            return Range1d(_min, _max)

    def get_axis(self, data: PlotInfo, axis: str):
        values = [avp.val for avp in getattr(data, f'{axis}_coords')]
        label = getattr(data, f'{axis}_coords')[0].attr.col_name
        if isinstance(values[0], str):
            ticker = CategoricalTicker()
            axis = CategoricalAxis(ticker=ticker, axis_label=label)
            return axis
        else:
            ticker = BasicTicker(num_minor_ticks=0)
            axis = LinearAxis(ticker=ticker, axis_label=label)
            return axis

    def get_tooltip(self, renderer, plot_info: PlotInfo) -> HoverTool:
        # TODO FIXME: check if there is a 'level' property
        x_colname = plot_info.x_coords[0].attr.col_name
        y_colname = plot_info.y_coords[0].attr.col_name

        additional = set(avp.attr.col_name + ': ' + avp.val for avp in chain(plot_info.x_seps, plot_info.y_seps))

        tooltip = f"""
        <div>
            <span style="font-size: 15px;">{x_colname}: @{x_colname}</span><br>
            <span style="font-size: 15px;">{y_colname}: @{y_colname}</span>
        </div>
        <div>
            <span style="font-size: 10px;">{'<br>'.join(additional)}</span><br>
        </div>
        """
        return HoverTool(tooltips=tooltip, anchor='top_center', renderers=[renderer])

    def display(self):
        grid = gridplot(self.plots, ncols=self.aggregator.ncols)
        show(grid)
