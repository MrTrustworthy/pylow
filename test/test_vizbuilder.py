import pathlib
from time import sleep

import pytest  # noqa
from pylow.data import VizConfig, Datasource, Attribute, Dimension, Measure
from pylow.data_preparation import Aggregator, AVP
from pylow.data_preparation.colorizer import adjust_brightness
from pylow.plotting import Plotter

from .config_builder import CONFIG_ROTATE, CONF_2d0m_1d1m_colM, CONF_2d0m_1d1m_colD

TESTDATA_PATH = pathlib.Path('test/data')  # as seen from project root
TEST_FILE = TESTDATA_PATH / 'testdata.csv'


@CONFIG_ROTATE
def test_config_builder(config, infos):
    pc = VizConfig.from_dict(config)
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
    pc = VizConfig.from_dict(config)

    ds = Datasource.from_csv(TEST_FILE.absolute())
    aggregator = Aggregator(ds, pc)
    aggregator.update_data()
    assert len(aggregator.data) == infos['plots']
    assert aggregator.ncols * aggregator.nrows == infos['plots']


@CONFIG_ROTATE
def test_viz(config, infos):
    pc = VizConfig.from_dict(config)
    ds = Datasource.from_csv(TEST_FILE.absolute())
    plotter = Plotter(ds, pc)
    plotter.create_viz()
    plotter.display()
    sleep(0.5)  # make sure the browser has time to render the temp file
    assert True


def test_color_lightning():
    base = '#1f77b4'
    with pytest.raises(Exception) as e_info:
        adjust_brightness('adfasdfasdf', 0.5)

    assert adjust_brightness(base, 9999999999) == '#ffffff'
    assert adjust_brightness(base, 0) == base


def test_output_coloring_measures():
    pc = VizConfig.from_dict(CONF_2d0m_1d1m_colM)
    ds = Datasource.from_csv(TEST_FILE.absolute())
    plotter = Plotter(ds, pc)
    plotter.aggregator.update_data()
    data = plotter.aggregator.data

    assert isinstance(data[0].colors, list)
    assert isinstance(data[0].colors[0], AVP)

    for plotinfo in data:
        assert len(plotinfo.colors) == len(plotinfo.x_coords) == len(plotinfo.y_coords)
        for i, region_avp in enumerate(plotinfo.x_coords):
            color = plotinfo.colors[i].val
            assert isinstance(color, str) and len(color) == 7


def test_output_coloring_dimensions():
    pc = VizConfig.from_dict(CONF_2d0m_1d1m_colD)
    ds = Datasource.from_csv(TEST_FILE.absolute())
    plotter = Plotter(ds, pc)
    plotter.aggregator.update_data()
    data = plotter.aggregator.data

    assert isinstance(data[0].colors, list)
    assert isinstance(data[0].colors[0], AVP)
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


def test_output_ordering():
    pc = VizConfig.from_dict(CONF_2d0m_1d1m_colD)
    ds = Datasource.from_csv(TEST_FILE.absolute())
    plotter = Plotter(ds, pc)
    plotter.aggregator.update_data()
    data = plotter.aggregator.data

    assert all(x.y_seps[-1].val == 'First Class' for x in data[0:3]), f'{[x.y_seps[-1].val for x in data[0:3]]}'
    assert all(x.y_seps[-1].val == 'Same Day' for x in data[3:6]), f'{x.y_seps[-1].val for x in data[3:6]}'
    assert all(x.y_seps[-1].val == 'Second Class' for x in data[6:9]), f'{x.y_seps[-1].val for x in data[6:9]}'
    assert all(x.y_seps[-1].val == 'Standard Class' for x in data[9:12]), f'{x.y_seps[-1].val for x in data[9:12]}'
    assert all(x.x_seps[-1].val == 'Furniture' for x in data[0::3]), f'{x.x_seps[-1].val for x in data[0::3]}'
    assert all(x.x_seps[-1].val == 'Office Supplies' for x in data[1::3]), f'{x.x_seps[-1].val for x in data[1::3]}'
    assert all(x.x_seps[-1].val == 'Technology' for x in data[2::3]), f'{x.x_seps[-1].val for x in data[2::3]}'


if __name__ == '__main__':
    pytest.main(['-s', 'test/test_vizbuilder.py'])
