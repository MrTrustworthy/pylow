import os
import pathlib
import sys
from time import sleep

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pylow  # noqa
import pytest  # noqa
from bokeh.io import show
from bokeh.models import ColumnDataSource, Line, Plot, Range1d



def test_flexline():

    data = {
        'x': [i for i in range(5)],
        'y': [i / 2 for i in range(5)],
        'size': [0.5 + (i * 0.25) for i in range(5)],
        'colors': [c for c in pylow.colorizer.ALL_COLORS[:5]]
    }

    source = ColumnDataSource(data=data)

    glyph = pylow.FlexLine(x='x', y='y')

    options = {
        'plot_width': 800,
        'plot_height': 600,
        'toolbar_location': None,
        'x_range': Range1d(0, 5),
        'y_range': Range1d(0, 4)
    }
    plot = Plot(**options)
    plot.add_glyph(source, glyph)
    show(plot)

if __name__ == '__main__':
    pytest.main(['-s', 'test/test_flexline.py'])
