from functools import partial

import matplotlib
import matplotlib.pyplot as plt
import mpld3
import numpy as np


def unique_list(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


class Plotter:

    def __init__(self, datasource, config):
        self.datasource = datasource
        self.config = config

    def create_frame(self):

        figure = plt.figure()
        axes = figure.add_subplot(1, 1, 1)

        conf = self.config
        columns = conf.columns
        rows = conf.rows
        aggregations = conf.aggregations
        draw_types = conf.draw_types
        colors = conf.colors

        for row, aggregation, draw_type, color in zip(rows, aggregations, draw_types, colors):

            # DATA PREPARATION
            relevant_data = self.datasource.data[row.col_name]

            # group on ALL columns!!
            groupings = [self.datasource.data[c.col_name] for c in columns]
            if len(groupings) == 0:
                groupings = lambda x: 0  # noqa return all as one group

            # perform grouping
            relevant_data = relevant_data.groupby(groupings)

            # perform aggregation
            aggregated_data = getattr(relevant_data, aggregation)()

            # draw
            draw_func = self._get_draw_func(axes, draw_type, aggregated_data)
            drawn_graph = draw_func(aggregated_data, picker=5)

            # DESIGN

            # set colors
            plt.setp(drawn_graph, color=color)

            self._handle_labeling(axes, columns, rows, aggregation, aggregated_data, color)
            figure.autofmt_xdate()  # TODO find out if usable on axes?!

        return figure

    def _handle_labeling(self, axes, columns, rows, aggregation, aggregated_data, color):
        # labels
        axes.set_xlabel(' / '.join(c.col_name for c in columns))
        axes.xaxis.set_label_position('top')
        axes.set_ylabel('{aggregation} of {measure}'.format(aggregation=aggregation, measure=rows[0].col_name))

        # ticks
        tick_labels = [t[-1] for t in aggregated_data.keys()]
        axes.set_xticks(list(range(len(tick_labels))))
        axes.set_xticklabels(tick_labels)
        axes.yaxis.label.set_color(color)

        for i in range(len(columns) - 1):
            # ticks on top
            # TODO reduce number of ticks to unique ticks
            axes2 = axes.twiny()
            # TODO Center top tick labels to the areas they apply to, without using the [''] + ... trick
            # see https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.tick_params.html

            tick2_labels = unique_list([''] + [t[i] for t in aggregated_data.keys()])  # no duplicates
            axes2.set_xticks(list(range(len(tick2_labels))))
            axes2.set_xticklabels(tick2_labels)

    def display(self, figure, *, export_file=None):

        if isinstance(export_file, str):
            html = mpld3.fig_to_html(figure)
            with open(export_file + '.html', 'w') as outfile:
                outfile.write(html)

        figure.show()  # NOTE immediately closes again if not blocked

    def _get_draw_func(self, axes, func_name, grouped_data):
        # data drawing
        draw_func = getattr(axes, func_name)
        if func_name == 'bar':
            ticks = list(range(len(grouped_data)))
            draw_func = partial(draw_func, ticks)
        return draw_func


def main():

    from datasource import Datasource

    ds = Datasource.from_csv('SalesJan2009.csv')
    ds.add_column('account_age', lambda x: x['Last_Login'] - x['Account_Created'])
    ds.add_column('Product C', lambda x: [s.strip() for s in x['Product']])
    create_frame(ds)


if __name__ == '__main__':
    main()
