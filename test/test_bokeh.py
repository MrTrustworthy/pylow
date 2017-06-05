import os
import pathlib
import sys
from time import sleep

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pylow  # noqa
import pytest  # noqa



TESTDATA_PATH = pathlib.Path('test/data')  # as seen from project root
TEST_FILE = TESTDATA_PATH / 'testdata.csv'

# Format Column<x dimensions, y measures> Rows<x dimensions, y measures>
CONF_1d0m_0d1m = {
    'columns': [pylow.Dimension('Category')],
    'rows': [pylow.Measure('Number of records')]
}
CONF_0d1m_1d0m = {
    'columns': [pylow.Measure('Number of records')],
    'rows': [pylow.Dimension('Category')]
}
CONF_2d0m_0d1m = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Measure('Quantity')]
}

CONF_2d0m_1d1m_colN = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
}

CONF_2d0m_1d1m_colD = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
    'color': pylow.Dimension('Region')
}

CONF_2d0m_1d1m_colM = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
    'color': pylow.Measure('Quantity')
}

CONF_2d0m_1d1m_sizeN = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
}

CONF_2d0m_1d1m_sizeD = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
    'size': pylow.Dimension('Region')
}

CONF_2d0m_1d1m_sizeM = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
    'size': pylow.Measure('Quantity')
}

CONF_2d0m_1d1m_sizeM_colD_line = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
    'size': pylow.Measure('Quantity'),
    'color': pylow.Dimension('Region'),
    'mark_type': pylow.plot_config.MarkType.LINE
}


CONF_2d0m_1d1m_sizeN_colN_circle = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
    'mark_type': pylow.plot_config.MarkType.CIRCLE
}

CONF_2d0m_1d1m_sizeN_colD_circle = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
    'color': pylow.Dimension('Region'),
    'mark_type': pylow.plot_config.MarkType.CIRCLE
}
CONF_2d0m_1d1m_sizeN_colM_circle = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
    'color': pylow.Measure('Quantity'),
    'mark_type': pylow.plot_config.MarkType.CIRCLE
}

CONF_2d0m_1d1m_sizeN_colDX_circle = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
    'color': pylow.Dimension('State'),
    'mark_type': pylow.plot_config.MarkType.CIRCLE
}
CONF_2d0m_1d1m_sizeN_colMX_circle = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')],
    'color': pylow.Measure('Profit'),
    'mark_type': pylow.plot_config.MarkType.CIRCLE
}

CONFIG_ROTATE = pytest.mark.parametrize("config,infos", [

    # (CONF_2d0m_1d1m_sizeN_colN_circle,
    #     {'dimensions': 3, 'measures': 1, 'plots': 12, 'color': None, 'color_sep': None}
    #  ),
    # (CONF_2d0m_1d1m_sizeN_colD_circle,
    #     {'dimensions': 3, 'measures': 1, 'plots': 12, 'color': 1, 'color_sep': None}
    #  ),
    (CONF_2d0m_1d1m_sizeN_colM_circle,
        {'dimensions': 3, 'measures': 1, 'plots': 12, 'color': 1, 'color_sep': None}
     ),
    # (CONF_2d0m_1d1m_sizeN_colDX_circle,
    #     {'dimensions': 4, 'measures': 1, 'plots': 12, 'color': None, 'color_sep': 1}
    #  ),
    (CONF_2d0m_1d1m_sizeN_colMX_circle, # FIXME color looks weird, check it out!
        {'dimensions': 3, 'measures': 2, 'plots': 12, 'color': 1, 'color_sep': None}
    )
])


@CONFIG_ROTATE
def test_config_builder(config, infos):
    pc = pylow.VizConfig.from_dict(config)
    assert len(pc.dimensions) == infos['dimensions']
    assert len(pc.measures) == infos['measures']

    # color and color sep are mutually exclusive
    assert pc.color is None or pc.color_sep is None

    if infos['color'] is None:
        assert pc.color is None
    else:
        assert pc.color is not None

    if infos['color_sep'] is None:
        assert pc.color_sep is None
    else:
        assert pc.color_sep is not None


@CONFIG_ROTATE
def test_aggregator(config, infos):
    pc = pylow.VizConfig.from_dict(config)

    ds = pylow.Datasource.from_csv(TEST_FILE.absolute())
    aggregator = pylow.Aggregator(ds, pc)
    aggregator.update_data()

    assert len(aggregator.data) == infos['plots']
    # expected_pis_in_pig = len(ds.get_variations_of(pc.color)) if pc.color is not None else 1
    # assert max(len(pig) for pig in aggregator.data) <= expected_pis_in_pig
    assert aggregator.ncols * aggregator.nrows == infos['plots']


@CONFIG_ROTATE
# @pytest.mark.skip()
def test_viz(config, infos):
    pc = pylow.VizConfig.from_dict(config)
    ds = pylow.Datasource.from_csv(TEST_FILE.absolute())
    plotter = pylow.BokehPlotter(ds, pc)
    plotter.create_viz()
    # assert len(plotter.plots) == plots
    plotter.display()
    sleep(0.5)  # make sure the browser has time to render the temp file
    assert True


@pytest.mark.skip()
def test_color_lightning():
    base = '#1f77b4'
    with pytest.raises(Exception) as e_info:
        pylow.adjust_brightness('adfasdfasdf', 0.5)

    assert pylow.adjust_brightness(base, 9999999999) == '#ffffff'
    assert pylow.adjust_brightness(base, 0) == base


@pytest.mark.skip()
def test_output_coloring_measures():
    pc = pylow.VizConfig.from_dict(CONF_2d0m_1d1m_colM)
    ds = pylow.Datasource.from_csv(TEST_FILE.absolute())
    plotter = pylow.BokehPlotter(ds, pc)
    plotter.aggregator.update_data()
    data = plotter.aggregator.data

    assert isinstance(data[0].colors, list)
    assert isinstance(data[0].colors[0], pylow.plotinfo.AVP)

    for plotinfo in data:
        assert len(plotinfo.colors) == len(plotinfo.x_coords) == len(plotinfo.y_coords)
        for i, region_avp in enumerate(plotinfo.x_coords):
            color = plotinfo.colors[i].val
            assert isinstance(color, str) and len(color) == 7


@pytest.mark.skip()
def test_output_coloring_dimensions():
    pc = pylow.VizConfig.from_dict(CONF_2d0m_1d1m_colD)
    ds = pylow.Datasource.from_csv(TEST_FILE.absolute())
    plotter = pylow.BokehPlotter(ds, pc)
    plotter.aggregator.update_data()
    data = plotter.aggregator.data

    assert isinstance(data[0].colors, list)
    assert isinstance(data[0].colors[0], pylow.plotinfo.AVP)
    reg_col = {  # first colors from colorizer.py
        'Central': '#1f77b4',
        'East': '#ff7f0e',
        'South': '#2ca02c',
        'West': '#d62728'
    }
    for plotinfo in data:
        assert len(plotinfo.colors) == len(plotinfo.x_coords) == len(plotinfo.y_coords)
        for i, region_avp in enumerate(plotinfo.x_coords):
            assert reg_col[region_avp.val] == plotinfo.colors[i].val


@pytest.mark.skip()
def test_output_ordering():
    pc = pylow.VizConfig.from_dict(CONF_2d0m_1d1m_colD)
    ds = pylow.Datasource.from_csv(TEST_FILE.absolute())
    plotter = pylow.BokehPlotter(ds, pc)
    plotter.aggregator.update_data()
    data = plotter.aggregator.data

    assert all(x.y_seps[-1].val == 'First Class' for x in data[0:3]), f'{[x.y_seps[-1].val for x in data[0:3]]}'
    assert all(x.y_seps[-1].val == 'Same Day' for x in data[3:6]), f'{x.y_seps[-1].val for x in data[3:6]}'
    assert all(x.y_seps[-1].val == 'Second Class' for x in data[6:9]), f'{x.y_seps[-1].val for x in data[6:9]}'
    assert all(x.y_seps[-1].val == 'Standard Class' for x in data[9:12]), f'{x.y_seps[-1].val for x in data[9:12]}'
    assert all(x.x_seps[-1].val == 'Furniture' for x in data[0::3]), f'{x.x_seps[-1].val for x in data[0::3]}'
    assert all(x.x_seps[-1].val == 'Office Supplies' for x in data[1::3]), f'{x.x_seps[-1].val for x in data[1::3]}'
    assert all(x.x_seps[-1].val == 'Technology' for x in data[2::3]), f'{x.x_seps[-1].val for x in data[2::3]}'

# @pytest.mark.skip()


if __name__ == '__main__':
    pytest.main(['-s', 'test/test_bokeh.py'])
