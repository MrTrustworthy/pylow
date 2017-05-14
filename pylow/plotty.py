from functools import partial
from typing import Any, List

import matplotlib
import matplotlib.pyplot as plt
import mpld3
import numpy as np
# for typing
import pandas
from typing import List, Dict, Optional, Sequence
from .datasource import Datasource
from .plot_config import Dimension, Measure, PlotConfig


def unique_list(seq: Sequence) -> List[Any]:
    seen = set()  # type: set
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]  # type: ignore


class Plotter:

    def __init__(self, datasource: Datasource, config: PlotConfig) -> None:
        self.datasource = datasource
        self.config = config

    def create_figure(self) -> matplotlib.figure.Figure:
        """ Creates a figure based on this instances datasource and configuration"""

        figure = matplotlib.pyplot.figure(figsize=(10, 6), dpi=96)
        axes = figure.add_subplot(1, 1, 1)  # type: matplotlib.axes.Axes

        for i, measure in enumerate(self.config.measures):

            # mirror axis for multiple measures to show all ticks
            if i > 0:  # FIXME does this work with >2 measures?
                axes = axes.twinx()

            # DATA PREPARATION
            relevant_data = self.datasource.data[measure.col_name]

            # group on ALL dimensions!!
            groupings = [self.datasource.data[dim.col_name] for dim in self.config.dimensions]  # type: Any
            if len(groupings) == 0:
                # groupby accepts a function too, return all data as one group named with the measures name
                groupings = lambda x: f'{measure.col_name}'

            # perform grouping
            relevant_data = relevant_data.groupby(groupings)

            # perform aggregation
            aggregated_data = getattr(relevant_data, measure.aggregation)()  # is a pandas object

            # draw
            drawn_graph = self._draw_data(axes, measure, aggregated_data)

            # DESIGN
            # set colors
            plt.setp(drawn_graph, color=measure.color)

            self._handle_labeling(axes, self.config.dimensions, i, measure, aggregated_data)
            figure.autofmt_xdate()  # TODO find out if usable on axes?!

        return figure

    def _draw_data(
        self,
        axes: matplotlib.axes.Axes,
        measure: Measure,
        aggregated_data: pandas.DataFrame
    ) -> matplotlib.artist.Artist:
        """ Draws the aggregated data onto an axes

        Arguments:
        ----------
        axes: matplotlib.axes.Axes
            The current axes to draw on
        measure: Measure
            The current measure
        aggregated_data: pandas.DataFrame
            The full aggregated data to draw

        Returns:
        ---------
        drawn_graph: matplotlib.artist.Artist
            The created artist for later manipulation
        """
        draw_func = getattr(axes, measure.draw_type)
        data_points = [datapoint for datapoint in aggregated_data]  # data to list via iterator
        if measure.draw_type == 'bar':
            ticks = list(range(len(data_points)))
            draw_func = partial(draw_func, ticks)
        drawn_graph = draw_func(data_points, **measure.options)
        return drawn_graph

    def _handle_labeling(
        self,
        axes: matplotlib.axis.Axis,
        dimensions: List[Dimension],
        number: int,
        measure: Measure,
        aggregated_data: pandas.DataFrame
    ) -> None:
        """ Draws labels for axes and ticks onto the figure

        Arguments:
        ----------
        axes: matplotlib.axis.Axis
            The current active axis
        dimensions: List[Dimension]
            All dimensions
        number: int
            The index of the measure to draw [0, n)
        measure: Measure
            The current measure to draw
        aggregated_data: pandas.DataFrame
            The aggregated data to draw (needed for extraction of dimension values)

        Returns:
        ---------
        None
        """
        # labels
        axes.set_xlabel(' / '.join(c.col_name for c in dimensions))
        axes.xaxis.set_label_position('top')

        y_label = f'{measure.aggregation} of {measure.col_name}'
        axes.set_ylabel(y_label, color=measure.color)

        # horizontal ticks
        tick_labels = self._get_tick_labels_from_aggregated_data(aggregated_data)

        for i, labels in enumerate(tick_labels[::-1]):
            curr_axis = axes if i == 0 else axes.twiny()
            labels = labels if i == 0 else [''] + unique_list(labels)  # second-level layer
            curr_axis.set_xticks(list(range(len(labels))))
            curr_axis.set_xticklabels(labels)

    def _get_tick_labels_from_aggregated_data(self, aggregated_data: pandas.DataFrame) -> List[List[str]]:
        """ Returns a list that contains a list for each aggregated dimension.

        Arguments
        ---------
        aggregated_data: pandas.DataFrame
            The Aggregated data that is about to be drawn
        Returns
        ---------
        labels: List[List[str]]
            Ex.: [['Product1', 'Product2', 'Product3']]
            Ex.: [['Product1', 'Product2', 'Product3'], ['Amex', 'Diners', 'Mastercard', 'Visa']]
        """
        label_details = aggregated_data.keys()  # pandas index or multiindex
        keys = [k for k in label_details]  # list of strings or list of tuples
        if keys == [0]:
            print(aggregated_data)
        if isinstance(keys[0], str):
            return [keys]

        levels = len(keys[0])
        labels = []
        for i in range(levels):
            level = []  # type: List[str]
            labels.append(level)
            for _tuple in keys:
                level.append(_tuple[i])
        return labels

    def display(self, figure: matplotlib.figure.Figure, *, export_file: str = None, wait: bool = False) -> None:
        """ Wrapper for the various ways to show a figure in matplotlib/mpld3

        Arguments:
        ----------
        figure : matplotlib.figure.Figure
            the figure to show

        Keyword arguments:
        ----------
        export_file : str
            if given, will export this figure as HTML file (default=None)
        wait : bool
            if True, will block execution until window is closed (default=False)

        Returns
        ---------
        None
        """

        if isinstance(export_file, str):
            html = mpld3.fig_to_html(figure)
            with open(export_file + '.html', 'w') as outfile:
                outfile.write(html)

        if wait:
            plt.show()
        else:
            # NOTE immediately closes again if not blocked
            figure.show()


if __name__ == '__main__':

    d = {
        'dimensions': [Dimension('Product')],
        'measures': [Measure('Price', color='r')]
    }
    config = PlotConfig.from_dict(d)

    d2 = {
        'dimensions': [Dimension('Product'), Dimension('Payment_Type')],
        'measures': [Measure('Price', draw_type='bar')]
    }
    config2 = PlotConfig.from_dict(d2)

    ds = Datasource.from_csv('test/data/SalesJan2009.csv')

    plotter = Plotter(ds, config)
    frame = plotter.create_figure()
    matplotlib.pyplot.show()

    plotter2 = Plotter(ds, config2)
    frame2 = plotter2.create_figure()
    matplotlib.pyplot.show()
