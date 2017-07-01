from math import pi
from typing import Any, Dict, Tuple

from bokeh.layouts import Column as BokehColumn
from bokeh.layouts import gridplot
from bokeh.models import (BasicTicker, CategoricalAxis, CategoricalTicker, ColumnDataSource, FactorRange, Grid,
                          LinearAxis, Plot, Range1d)
from bokeh.models.annotations import Label, Title
from bokeh.models.axes import Axis
from bokeh.models.ranges import Range
from bokeh.models.tickers import Ticker

from pylow.data.datasource import Datasource
from pylow.data.vizconfig import VizConfig
from pylow.data_preparation.aggregator import Aggregator
from pylow.data_preparation.plotinfo import PlotInfo
from pylow.plotting.glyph_factory import create_glyph
from pylow.plotting.tooltip_factory import generate_tooltip
from pylow.utils import unique_list


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

        source = ColumnDataSource(data=plot_info.get_viz_data())

        # RANGES
        x_range, y_range = self._get_range(plot_info, 'x'), self._get_range(plot_info, 'y')

        options = self._get_plot_options(plot_info, x_range, y_range)
        plot = Plot(**options)

        self._add_labels(plot, plot_info, options)

        # AXES
        self._add_axes_and_grids(plot, plot_info)

        # GLYPH
        glyph = create_glyph(self.aggregator.config.mark_type, plot_info.column_names)
        renderer = plot.add_glyph(source, glyph)

        # HOVER
        hover = generate_tooltip(renderer, plot_info)
        plot.add_tools(hover)
        return plot

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

        # set title on top if it's in the top middle
        if self.aggregator.is_in_center_top_column(plot_info):
            # TODO multiple titles for multiple layers of dimensions
            # FIXME this needs its own function
            x_coord_col_name = plot_info.get_example_avp_for_axis('x').attr.col_name
            x_seps_col_names = [sep.attr.col_name for sep in plot_info.x_seps]
            text = '/'.join(x_seps_col_names + [x_coord_col_name])
            options['title'] = Title(text=text, align='center')

        return options

    def _add_labels(self, plot: Plot, plot_info: PlotInfo, options: Dict[str, Any]) -> None:
        """ Adds the labels to the left and top of a plot depending on its position in the grid"""

        # Labels on the left
        if self.aggregator.is_in_first_column(plot_info):
            # TODO can we use plotinfo.example_val... here?
            text = plot_info.get_axis_label('y')
            label = Label(x=0, y=options['plot_height'] // 2, x_units='screen',
                          y_units='screen', text=text, render_mode='css', text_align='right')
            plot.add_layout(label)

        # Labels top
        # if there are no x_seps (aka only one column), there is no need to draw additional labels
        if self.aggregator.is_in_first_row(plot_info) and len(plot_info.x_seps) > 0:
            # TODO can we use plotinfo.example_val... here?
            text = plot_info.get_axis_label('x')
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

        # Don't create grid lines for dimensions, only for measures
        # TODO FIXME figure out how to do this the best way, is currently only based on IS_STRING
        value = plot_info.get_example_avp_for_axis('x').val
        if not isinstance(value, str):
            grid = Grid(dimension=0, ticker=x_tick, grid_line_dash='dotted')
            plot.add_layout(grid)

        value = plot_info.get_example_avp_for_axis('y').val
        if not isinstance(value, str):
            grid = Grid(dimension=1, ticker=y_tick, grid_line_dash='dotted')
            plot.add_layout(grid)

    def _get_range(self, plot_info: PlotInfo, axis: str) -> Range:
        """ Creates a bokeh.Range object for the given axis & plot_info"""

        # TODO FIXME check based on dimension/measure instead of IS_STR
        values = unique_list([avp.val for avp in getattr(plot_info, f'{axis}_coords')])
        if len(values) == 0:
            # handle the case of 0d0m-configs
            values = [plot_info.get_example_avp_for_axis(axis).val]

        if isinstance(values[0], str):
            return FactorRange(*values)
        else:
            _min, _max = getattr(self.aggregator, f'{axis}_min'), getattr(self.aggregator, f'{axis}_max')
            if _min == _max:
                _min = 0
            return Range1d(_min, _max)

    def _get_axis(self, data: PlotInfo, axis: str) -> Tuple[Ticker, Axis]:
        """ Creates and returns the axies object for a given axis direction & data"""

        options = {
            'major_tick_in': 0,
            'major_tick_out': 0
        }
        # only show the axis labels left, never at the bottom
        if axis == 'y':
            sample_colname = data.get_example_avp_for_axis(axis).attr.col_name
            options['axis_label'] = sample_colname

        sample_value = data.get_example_avp_for_axis(axis).val
        if isinstance(sample_value, str):
            ticker = CategoricalTicker()
            axis = CategoricalAxis(ticker=ticker, major_label_orientation=pi / 2, **options)
        else:
            ticker = BasicTicker(num_minor_ticks=0)
            axis = LinearAxis(ticker=ticker, **options)

        return ticker, axis

    def get_output(self) -> BokehColumn:
        """ Displays all generated plots in a grid"""

        grid = gridplot(self.plots, ncols=self.aggregator.ncols)
        return grid
