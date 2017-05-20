
from collections import defaultdict

from bokeh.layouts import GridSpec, gridplot
from bokeh.models import (BasicTickFormatter, CategoricalTickFormatter,
                          FixedTicker, FuncTickFormatter, NumeralTickFormatter,
                          TickFormatter)
from bokeh.models.ranges import FactorRange
from bokeh.plotting import figure, output_file, show
from bokeh.plotting.helpers import _get_range

from .datasource import Datasource
from .plot_config import Dimension, Measure, PlotConfig


# self.figure.xaxis[0].formatter = LabelFormatter(indicie_labels)
# class LabelFormatter(FuncTickFormatter):
#     def __init__(self, labels):
#         base_code = f'return {str(labels)}[tick]'
#
#         super().__init__(code=base_code)


class BokehPlotter():

    def __init__(self, datasource, config):
        self.datasource = datasource
        self.config = config
        self.figures = []

    def create_viz(self):

        data = self.datasource.data

        for measure in self.config.measures:

            column_dimensions = [c for c in self.config.columns if isinstance(c, Dimension)]



            bk_figure = figure(
                x_axis_label=' / '.join(m.col_name for m in column_dimensions),
                y_axis_label=measure.col_name,
                x_range=['x']  # FIXME needed so a factorrange is created initially
            )
            self.figures.append(bk_figure)

            # TODO FIXME Try low-level API or split into different frames

            # data aggregation
            grouped_data = data.groupby([c.col_name for c in column_dimensions])[measure.col_name]
            aggregated_data = getattr(grouped_data, measure.aggregation)()  # is a pandas object
            formatted_data = self._reformat_aggregated_data(aggregated_data)

            self._draw_dict(formatted_data, bk_figure, measure)

            # for row in self.config.rows:
            #     if isinstance(row, Measure):
            #         continue

    def _draw_dict(self, formatted_data, bk_figure, measure):

        key, value = list(formatted_data.items())[0]
        if isinstance(value, dict):
            for key, value in formatted_data.items():
                self._draw_dict(formatted_data[key], bk_figure, measure)
        else:  # FIXME check if its numpy.int64
            self._paint_plot(formatted_data, bk_figure, measure)

    def _paint_plot(self, draw_data, bk_figure, measure):
        # FIXME replace after update
        plot_data = list(draw_data.values())
        plot_ticks = list(draw_data.keys())
        bk_figure.x_range.factors = plot_ticks
        glyph = bk_figure.line(
            plot_ticks,
            plot_data,
            legend=measure.col_name,
            line_color=measure.color
        )

    def _reformat_aggregated_data(self, aggregated_data):
        """ Turns aggregated data into a format like below

        {'Furniture': {'Central': 60, 'East': 44, 'South': 71, 'West': 52}, 'Office Supplies': {'Central':...
        """
        data_struct = aggregated_data.to_dict()  # Dict[Tuple(str), int] or Dict[str, int]

        # unify format to  Dict[Tuple(str), int] instead of sometimes Dict[str, int]
        if isinstance(list(data_struct.keys())[0], str):
            data_struct = {(key, ): value for key, value in data_struct.items()}

        # force into a list of tuples
        data_struct = [tuple([*keys, value]) for keys, value in data_struct.items()]

        output_dict = {}
        for all_values in data_struct:

            key_values = all_values[:-1]
            current_level_dict = output_dict

            # go through each level of tuples until the next-to-last and fill a dictionary
            for i, key in enumerate(key_values):

                # if on the next-to-last level, fill in the value
                if i + 1 == len(key_values):
                    current_level_dict[key] = all_values[-1]
                    continue

                if not key in current_level_dict:
                    current_level_dict[key] = {}
                current_level_dict = current_level_dict[key]

        return output_dict

    def display(self, *, export_file=None, wait=True):
        grid = gridplot([self.figures])
        show(grid)

if __name__ == '__main__':
    import pytest
    pytest.main()

    #
    # def _create_figures(self):
    #     data = self.datasource.data
    #
    #     # TODO Image testcases for tableau configurations
    #
    #     for measure in self.config.measures:
    #
    #         bk_figure = figure(
    #             title='Generated Plot',
    #             x_axis_label=' / '.join(m.col_name for m in self.config.dimensions),
    #             y_axis_label=' / '.join(m.col_name for m in self.config.measures),
    #             x_range=['x']  # FIXME needed so a factorrange is created initially, as creating one later doesnt work
    #         )
    #         self.figures.append(bk_figure)
    #         bk_figure.yaxis[0].formatter = BasicTickFormatter(use_scientific=False)
    #
    #         grouped_data = data.groupby([c.col_name for c in self.config.dimensions])[measure.col_name]
    #         aggregated_data = getattr(grouped_data, measure.aggregation)()  # is a pandas object
    #
    #         # FIXME replace after update
    #         indicie_labels = list(aggregated_data.to_dict().keys())
    #         bk_figure.x_range.factors = indicie_labels  # changing range object directly doesnt work
    #
    #         # indicie_labels = list(aggregated_data.to_dict().keys())
    #         # indicies = list(range(len(indicie_labels)))
    #         # label_overrides = {k: v for k,v in zip(indicies, indicie_labels)}
    #         # # draw glyph with indicies instead of indicie_labels
    #         # bk_figure.xaxis.major_label_overrides = label_overrides
    #
    #         glyph = bk_figure.line(indicie_labels, aggregated_data.tolist(),
    #                                legend=measure.col_name, line_color=measure.color)
    #
    #     # figure.title('Yooo')
