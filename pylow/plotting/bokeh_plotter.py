from itertools import chain
from typing import Any, Dict, Tuple

from bokeh.core.properties import field
from bokeh.io import show
from bokeh.layouts import gridplot
from bokeh.models import (BasicTicker, CategoricalAxis, CategoricalTicker,
                          ColumnDataSource, FactorRange, Grid,
                          HoverTool, LinearAxis, Plot, Range1d)
from bokeh.models.annotations import Label, Title
from bokeh.models.axes import Axis
from bokeh.models.glyphs import Circle, Glyph, VBar
from bokeh.models.ranges import Range
from bokeh.models.tickers import Ticker

from pylow.data.datasource import Datasource
from pylow.data.vizconfig import VizConfig
from pylow.data_preparation.aggregator import Aggregator
from pylow.data_preparation.plotinfo import PlotInfo
from pylow.extensions.flexline import FlexLine
from pylow.utils import unique_list, MarkType


class Plotter:
    def __init__(self, datasource: Datasource, config: VizConfig):
        self.aggregator = Aggregator(datasource, config)
        self.plots = []

    def create_viz(self) -> None:
        """ The single external interface for consumers; will create all plots of this instance"""
        self.aggregator.update_data()
        data = self.aggregator.data

        for plotinfo in data:
            plot = self._make_plot(plotinfo)
            self.plots.append(plot)

    def _make_plot(self, plot_info: PlotInfo) -> Plot:
        """ Main function that orchestrates the creation of a bokeh.Plot object.

        Will delegate the parts of plot creation to other methods
        """

        x_colname, y_colname, color_colname, size_colname, source = self._prepare_viz_data(plot_info)

        # RANGES
        x_range, y_range = self._get_range(plot_info, 'x'), self._get_range(plot_info, 'y')

        options = self._get_plot_options(plot_info, x_range, y_range)
        plot = Plot(**options)

        self._add_labels(plot, plot_info, options)

        # AXES
        self._add_axes_and_grids(plot, plot_info)

        # GLYPH
        glyph = self._create_glyph(x_colname, y_colname, color_colname, size_colname)
        renderer = plot.add_glyph(source, glyph)

        # HOVER
        hover = self._get_tooltip(renderer, plot_info)
        plot.add_tools(hover)
        return plot

    def _prepare_viz_data(self, plot_info: PlotInfo) -> Tuple[str, str, str, str, ColumnDataSource]:
        """ Create a representation of the data for plotting that is suitable for consumption by bokeh"""

        x_colname, y_colname, color_colname, size_colname, data = plot_info.get_viz_data(self.aggregator.config)
        source = ColumnDataSource(data=data)
        return x_colname, y_colname, color_colname, size_colname, source

    def _get_plot_options(self, plot_info: PlotInfo, x_range: Range, y_range: Range) -> Dict[str, Any]:
        """ Create the configuration object to instantiate a bokeh.Plot object"""

        options = {
            'plot_width': int(1200 / self.aggregator.ncols),
            'plot_height': int(800 / self.aggregator.nrows),
            'toolbar_location': None,
            'x_range': x_range,
            'y_range': y_range,
            'min_border': 0,
            'min_border_left': 0 if self.aggregator.is_in_first_column(plot_info) else 0
        }
        # title top
        if self.aggregator.is_in_center_top_column(plot_info):
            # TODO multiple titles for multiple layers of dimensions
            text = '/'.join(sep.attr.col_name for sep in chain(plot_info.x_seps, [plot_info.x_coords[0]]))
            options['title'] = Title(text=text, align='center')

        return options

    def _add_labels(self, plot: Plot, plot_info: PlotInfo, options: Dict[str, Any]) -> None:
        """ Adds the labels to the left and top of a plot depending on its position in the grid"""

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

    def _add_axes_and_grids(self, plot: Plot, plot_info: PlotInfo) -> None:
        """ Adds the axes and grids to the plot, depending on its position in the grid"""

        x_tick, x_ax = self._get_axis(plot_info, 'x')
        if self.aggregator.is_in_last_row(plot_info):
            plot.add_layout(x_ax, 'below')

        y_tick, y_ax = self._get_axis(plot_info, 'y')
        if self.aggregator.is_in_first_column(plot_info):
            plot.add_layout(y_ax, 'left')

        # Don't create grid lines for dimensions
        # TODO FIXME figure out how to do this the best way, is currently only based on IS_STRING
        value = [avp.val for avp in plot_info.x_coords][0]
        if not isinstance(value, str):
            grid = Grid(dimension=0, ticker=x_tick, grid_line_dash='dotted')
            plot.add_layout(grid)

        value = [avp.val for avp in plot_info.y_coords][0]
        if not isinstance(value, str):
            grid = Grid(dimension=1, ticker=y_tick, grid_line_dash='dotted')
            plot.add_layout(grid)

    def _create_glyph(self, x_colname: str, y_colname: str, color_colname: str, size_colname: str) -> Glyph:
        """ Creates a glyph based on the configuration"""

        mark_type = self.aggregator.config.mark_type
        if mark_type == MarkType.LINE:
            return FlexLine(
                x=field(x_colname),
                y=field(y_colname),
                size=field(size_colname),
                colors=field(color_colname)
            )
        elif mark_type == MarkType.BAR:
            return VBar(
                x=field(x_colname),
                top=field(y_colname),
                fill_color=field(color_colname),
                line_color=field(color_colname),
                width=field(size_colname)
            )
        elif mark_type == MarkType.CIRCLE:
            return Circle(
                x=field(x_colname),
                y=field(y_colname),
                fill_color=field(color_colname),
                line_color=field(color_colname),
                size=field(size_colname)
            )
        else:
            assert False, f'VizConfig.mark_type must be one of {MarkType}'

    def _get_range(self, data: PlotInfo, axis: str) -> Range:
        """ Creates a bokeh.Range object for the given axis & data"""

        # TODO FIXME check based on dimension/measure instead of IS_STR
        values = unique_list([avp.val for avp in getattr(data, f'{axis}_coords')])
        if isinstance(values[0], str):
            return FactorRange(*values)
        else:
            _min, _max = getattr(self.aggregator, f'{axis}_min'), getattr(self.aggregator, f'{axis}_max')
            return Range1d(_min, _max)

    def _get_axis(self, data: PlotInfo, axis: str) -> Tuple[Ticker, Axis]:
        """ Creates and returns the axies object for a given axis direction & data"""

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

    def _get_tooltip(self, renderer, plot_info: PlotInfo) -> HoverTool:
        """ Creates and returns the tooltip-template for this plot"""

        # TODO FIXME: Figure out how to approach this, currently basically only a tech demo
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
        """ Displays all generated plots in a grid"""

        grid = gridplot(self.plots, ncols=self.aggregator.ncols)
        show(grid)
