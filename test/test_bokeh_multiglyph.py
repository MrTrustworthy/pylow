import os
import pathlib
import string
import sys
from time import sleep

import pytest
from bokeh.io import show
from bokeh.models import (Circle, ColumnDataSource, CategoricalAxis, FactorRange, LinearAxis, Plot,
                          Range1d)


def test_flexline():

    data = {
        'x1': [string.ascii_letters[i] for i in range(7)],
        'y1': [i**0.5 for i in range(7)],
        'x2': [string.ascii_letters[i] for i in range(7)],
        'y2': [i**0.5 + 10 for i in range(7)],
        'size': [10 + (i * 5) for i in range(7)],
    }

    source = ColumnDataSource(data=data)

    glyph1 = Circle(x='x1', y='y1')
    glyph2 = Circle(x='x2', y='y2')

    options = {
        'plot_width': 800,
        'plot_height': 600,
        'toolbar_location': None,
        'x_range': FactorRange(*data['x1']),
        'y_range': Range1d(-1, 20)
    }
    plot = Plot(**options)
    plot.add_glyph(source, glyph1)
    plot.add_glyph(source, glyph2)

    plot.add_layout(CategoricalAxis(), 'below')
    plot.add_layout(LinearAxis(), 'left')
    show(plot)

if __name__ == '__main__':
    pytest.main(['-s', 'test_bokeh_multiglyph.py'])
