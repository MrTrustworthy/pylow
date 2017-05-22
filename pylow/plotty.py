from functools import partial
from typing import Any, Dict, List, Optional, Sequence, Union

import matplotlib
import matplotlib.pyplot as plt
import mpld3
import numpy as np
# for typing
import pandas

from .datasource import Datasource
from .plot_config import Dimension, Measure, VizConfig


def unique_list(seq: Sequence) -> List[Any]:
    seen = set()  # type: set
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]  # type: ignore


def cache_wrapper(func):
    cache = {}  # NOTE shares through all instances of cache_wrapper wraps

    def wrapped(*args, **kwargs):
        return func(*args, cache=cache, **kwargs)
    return wrapped


def get_nonhighlight_color(element, *, amount=0.2):
    _r, _g, _b, _a = get_element_color(element)  # tuple with (r, g, b, a)
    r = _r if _r >= 1 else _r - amount
    g = _g if _g >= 1 else _g - amount
    b = _b if _b >= 1 else _b - amount
    return (r, g, b, _a)


def get_highlight_color(element, *, amount=0.2):
    _r, _g, _b, _a = get_element_color(element)  # tuple with (r, g, b, a)
    print('in', (_r, _g, _b, _a))
    r = _r if _r >= (1 - amount) else _r + amount
    g = _g if _g >= (1 - amount) else _g + amount
    b = _b if _b >= (1 - amount) else _b + amount
    print('out', (r, g, b, _a))

    return (r, g, b, _a)


def get_element_color(element: matplotlib.artist.Artist) -> Any:
    """ Returns the color of an artist

    Arguments:
    ----------
    element: matplotlib.artist.Artist
        The artist that needs its color extracted

    Returns:
    ---------
    actor_color: Any
        The actors color. May be string (ex. 'b'), tuple (length 3 or 4), hexcode, ...
    """

    for call in ('get_color', 'get_facecolor'):
        if hasattr(element, call):
            return getattr(element, call)()  # FIXME can also be 'b' instead of tuple ....


class Plotter:

    def __init__(self, datasource: Datasource, config: VizConfig) -> None:
        self.datasource = datasource
        self.config = config
        self.artists = []  # type: List[matplotlib.artist.Artist]
        self.figure = None  # type: Optional[matplotlib.figure.Figure]

    def create_figure(self) -> matplotlib.figure.Figure:
        """ Creates a figure based on this instances datasource and configuration"""

        self.figure = matplotlib.pyplot.figure(figsize=(10, 6), dpi=96)
        self.figure.canvas.mpl_connect('motion_notify_event', self._dispatch_events)
        self.figure.autofmt_xdate()  # TODO find out if usable on axes?!

        axes = self.figure.add_subplot(1, 1, 1)  # type: matplotlib.axes.Axes
        self.artists.clear()  # TODO FIXME

        for i, measure in enumerate(self.config.measures):

            # mirror axis for multiple measures to show all ticks
            if i > 0:  # FIXME does this work with >2 measures?
                axes = axes.twinx()

            axes.patch.set_alpha(0.0)  # fix for mpld3 https://github.com/mpld3/mpld3/issues/188

            aggregated_data = self._prepare_data(measure)

            # draw
            # TODO find out what exactly drawn_graphs is for (bar, plot, ...)
            drawn_graphs = self._draw_data(axes, measure, aggregated_data)
            for elem in drawn_graphs:
                self.artists.append(elem)
            # DESIGN
            plt.setp(drawn_graphs, color=measure.color)
            self._handle_labeling(axes, self.config.dimensions, i, measure, aggregated_data)

    def _prepare_data(self, measure: Measure) -> pandas.DataFrame:
        """ Groups and aggregates the data based on all dimensions and a given measure

        Arugments:
        ----------
        measure: Measure
            The relevant measure that will be aggregated

        Returns:
        ---------
        aggregated_data: pandas.DataFrame
            The grouped and aggregated data, ready for display
        """
        relevant_data = self.datasource.data[measure.col_name]

        # get grouping columns
        groupings = [self.datasource.data[dim.col_name] for dim in self.config.dimensions]  # type: Any
        if len(groupings) == 0:
            # groupby() accepts a function too, return all data as one group named with the measures name
            groupings = lambda x: f'{measure.col_name}'

        grouped_data = relevant_data.groupby(groupings)
        aggregated_data = getattr(grouped_data, measure.aggregation)()  # is a pandas object
        return aggregated_data

    @cache_wrapper
    def _dispatch_events(self, event: matplotlib.backend_bases.MouseEvent, cache: dict=None) -> None:
        """ Handles 'motion_notify_event's on the figure and dispatches the event handlers

        Arugments:
        ----------
        event: matplotlib.backend_bases.MouseEvent
            The event that was fired on mouse movement
        cache: dict
            Argument that is passed via @cache_wrapper and contains the last hit
        """
        is_affected_elem = lambda elem: elem.contains(event)[0]  # contains() returns (truth, details) tuple
        hovered_elements = list(filter(is_affected_elem, self.artists))

        previous_hit = cache.get('last_hit', None)
        # the last should always be the element drawn on top
        hit = hovered_elements[-1] if len(hovered_elements) != 0 else None

        # send mouse enter and leave events
        if hit is not None:
            if previous_hit is not None:
                if hit == previous_hit:
                    return
                else:
                    self._on_mouseleave(previous_hit)

            self._on_mouseenter(hit)
            cache['last_hit'] = hit
        else:
            if previous_hit is not None:
                self._on_mouseleave(previous_hit)
                cache['last_hit'] = None

    def _on_mouseenter(self, element: matplotlib.artist.Artist) -> None:
        """ Handles events where the mouse enters an artist

        Arguments:
        ----------
        element: matplotlib.artist.Artist the artist that the mouse entered on
        """
        current_color = get_element_color(element)
        element._tapylow_old_color = current_color
        element.set_color('aquamarine')
        self.figure.canvas.draw()

    def _on_mouseleave(self, element: matplotlib.artist.Artist) -> None:
        """ Handles events where the mouse leaves an artist

        Arguments:
        ----------
        element: matplotlib.artist.Artist the artist that the mouse left
        """
        element.set_color(element._tapylow_old_color)
        self.figure.canvas.draw()

    def _draw_data(
        self,
        axes: matplotlib.axes.Axes,
        measure: Measure,
        aggregated_data: pandas.DataFrame
    ) -> Union[matplotlib.container.BarContainer, List[matplotlib.lines.Line2D]]:
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

        drawn_graph = draw_func(data_points, picker=5, **measure.options)
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

    def display(self, *, export_file: str = None, wait: bool = False) -> None:
        """ Wrapper for the various ways to show a figure in matplotlib/mpld3.

        Always shows the figure of the instance.

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
            html = mpld3.fig_to_html(self.figure)
            with open(export_file + '.html', 'w') as outfile:
                outfile.write(html)

        if wait:
            plt.show()
        else:
            # NOTE immediately closes again if not blocked
            self.figure.show()


if __name__ == '__main__':

    d = {
        'dimensions': [Dimension('Product')],
        'measures': [Measure('Price', color='r')]
    }
    config = VizConfig.from_dict(d)

    d2 = {
        'dimensions': [Dimension('Product'), Dimension('Payment_Type')],
        'measures': [Measure('Price', draw_type='bar')]
    }
    config2 = VizConfig.from_dict(d2)

    ds = Datasource.from_csv('test/data/SalesJan2009.csv')

    plotter = Plotter(ds, config)
    frame = plotter.create_figure()
    matplotlib.pyplot.show()

    plotter2 = Plotter(ds, config2)
    frame2 = plotter2.create_figure()
    matplotlib.pyplot.show()
