
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
from bokeh.models.annotations import Label, Title
from bokeh.models.axes import Axis
from bokeh.models.glyphs import Circle, Glyph, Line, Text, VBar
from bokeh.models.ranges import Range
from bokeh.models.tickers import Ticker
from bokeh.sampledata.sprint import sprint

from .aggregator import Aggregator
from .datasource import Datasource
from .plot_config import Attribute, Dimension, MarkType, Measure, VizConfig
from .plotinfo import AVP, PlotInfo
from .utils import make_unique_string_list


class BokehPlotter:

    def __init__(self, datasource: Datasource, config: VizConfig):
        self.aggregator = Aggregator(datasource, config)
        self.plots = []

    def create_viz(self) -> None:
        self.aggregator.update_data()
        data = self.aggregator.data

        for plotinfo in data:
            plot = self.make_plot(plotinfo)
            self.plots.append(plot)

    def make_plot(self, plot_info: PlotInfo) -> None:

        x_colname = plot_info.x_coords[0].attr.col_name
        y_colname = plot_info.y_coords[0].attr.col_name
        color_colname = '_color'
        size_colname = '_size'
        # DATA
        data = {
            x_colname: [avp.val for avp in plot_info.x_coords],
            y_colname: [avp.val for avp in plot_info.y_coords],
            color_colname: [avp.val for avp in plot_info.colors],
            size_colname: [self.aggregator.config.get_glyph_size(avp.val) for avp in plot_info.sizes]
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
            'min_border': 0,
            'min_border_left': 0 if self.aggregator.is_in_first_column(plot_info) else 0
        }
        # title top
        if self.aggregator.is_in_center_top_column(plot_info):
            # TODO multiple titles for multiple layers of dimensions
            text = '/'.join(sep.attr.col_name for sep in chain(plot_info.x_seps, [plot_info.x_coords[0]]))
            options['title'] = Title(text=text, align='center')

        plot = Plot(**options)

        # Labels on the left
        if self.aggregator.is_in_first_column(plot_info):
            text = plot_info.y_seps[-1].val.replace(' ', '\n')  # FIXME inserting \n does nothing
            label = Label(x=0, y=options['plot_height'] // 2, x_units='screen',
                          y_units='screen', text=text, render_mode='css', text_align='right')
            plot.add_layout(label)

        # Labels top
        if self.aggregator.is_in_first_row(plot_info):
            text = plot_info.x_seps[-1].val
            label = Label(x=options['plot_width'] // 2, y=options['plot_height'], x_units='screen',
                          y_units='screen', text=text, render_mode='css', text_align='center')
            plot.add_layout(label)

        # AXES
        self.make_axes_and_grids(plot, plot_info)

        # GLYPH
        glyph = self.create_glyph(x_colname, y_colname, color_colname, size_colname)
        renderer = plot.add_glyph(source, glyph)

        # HOVER
        hover = self.get_tooltip(renderer, plot_info)
        plot.add_tools(hover)
        return plot

    def make_axes_and_grids(self, plot: Plot, plot_info: PlotInfo) -> None:
        x_tick, x_ax = self.get_axis(plot_info, 'x')
        if self.aggregator.is_in_last_row(plot_info):
            plot.add_layout(x_ax, 'below')

        y_tick, y_ax = self.get_axis(plot_info, 'y')
        if self.aggregator.is_in_first_column(plot_info):
            plot.add_layout(y_ax, 'left')

        value = [avp.val for avp in plot_info.x_coords][0]
        if not isinstance(value, str):
            grid = Grid(dimension=0, ticker=x_tick, grid_line_dash='dotted')
            plot.add_layout(grid)

        value = [avp.val for avp in plot_info.y_coords][0]
        if not isinstance(value, str):
            grid = Grid(dimension=1, ticker=y_tick, grid_line_dash='dotted')
            plot.add_layout(grid)

    def create_glyph(self, x_colname: str, y_colname: str, color_colname: str, size_colname: str) -> Glyph:
        mark_type = self.aggregator.config.mark_type
        if mark_type == MarkType.LINE:
            return Line(x=x_colname, y=y_colname)
        elif mark_type == MarkType.BAR:
            return VBar(x=x_colname, top=y_colname, fill_color=color_colname, line_color=color_colname, width=size_colname)
        elif mark_type == MarkType.CIRCLE:
            return Circle(x=x_colname, y=y_colname, fill_color=color_colname, line_color=color_colname, size=size_colname)
        else:
            assert False, f'VizConfig.mark_type must be one of {MarkType}'

    def get_range(self, data: PlotInfo, axis: str) -> Range:
        values = [avp.val for avp in getattr(data, f'{axis}_coords')]
        if isinstance(values[0], str):
            return FactorRange(*values)
        else:
            _min, _max = getattr(self.aggregator, f'{axis}_min'), getattr(self.aggregator, f'{axis}_max')
            return Range1d(_min, _max)

    def get_axis(self, data: PlotInfo, axis: str) -> Tuple[Ticker, Axis]:

        values = [avp.val for avp in getattr(data, f'{axis}_coords')]
        options = {
            'major_tick_in': 0,
            'major_tick_out': 0
        }
        # only show the axis labels left, never at the bottom
        if axis == 'y':
            options['axis_label'] = getattr(data, f'{axis}_coords')[0].attr.col_name

        if isinstance(values[0], str):
            ticker = CategoricalTicker()
            axis = CategoricalAxis(ticker=ticker, major_label_orientation=1.57, **options)
        else:
            ticker = BasicTicker(num_minor_ticks=0)
            axis = LinearAxis(ticker=ticker, **options)

        return ticker, axis

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

    def display(self) -> None:
        grid = gridplot(self.plots, ncols=self.aggregator.ncols)
        show(grid)
