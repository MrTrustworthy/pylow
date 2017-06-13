import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pylow  # noqa
import pytest  # noqa
from bokeh.io import show
from bokeh.models import ColumnDataSource, Plot, Range1d, LinearAxis


def test_flexline():
    data = {
        'x': [i for i in range(7)],
        'y': [i ** 0.5 for i in range(7)],
        'size': [10 + (i * 5) for i in range(7)],
        'colors': [c for c in pylow.colorizer.ALL_COLORS[:7]]
    }

    source = ColumnDataSource(data=data)

    glyph = pylow.FlexLine(x='x', y='y', size='size', colors='colors')

    options = {
        'plot_width': 800,
        'plot_height': 600,
        'toolbar_location': None,
        'x_range': Range1d(-1, 7),
        'y_range': Range1d(-1, 3)
    }
    plot = Plot(**options)
    plot.add_glyph(source, glyph)
    plot.add_layout(LinearAxis(), 'below')
    plot.add_layout(LinearAxis(), 'left')
    show(plot)


if __name__ == '__main__':
    pytest.main(['-s', 'test/test_flexline.py'])
