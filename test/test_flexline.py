import pytest
from bokeh.models import ColumnDataSource, Plot, Range1d, LinearAxis

from pylow.data_preparation import colorizer
from pylow.extensions.flexline import FlexLine
from .testutils import save_plot_temp


def test_flexline():
    data = {
        'x': [i for i in range(7)],
        'y': [i ** 0.5 for i in range(7)],
        'size': [10 + (i * 5) for i in range(7)],
        'colors': [c for c in colorizer.ALL_COLORS[:7]]
    }

    source = ColumnDataSource(data=data)

    glyph = FlexLine(x='x', y='y', size='size', colors='colors')

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
    save_plot_temp(plot, 'multiglyph')


if __name__ == '__main__':
    pytest.main(['-s', 'test/test_flexline.py'])
