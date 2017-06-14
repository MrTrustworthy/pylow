import os
import pathlib
import pytest
from pylow.data import VizConfig, Datasource
from pylow.data_preparation import Aggregator
from pylow.plotting import Plotter
from .config_builder import CONFIG_ROTATE
from bokeh.io import save

TEMP_FOLDER = pathlib.Path('test/temp')

TESTDATA_PATH = pathlib.Path('test/data')  # as seen from project root
TEST_FILE = TESTDATA_PATH / 'testdata.csv'
# only instantiate once for better performance
DATASOURCE = Datasource.from_csv(TEST_FILE.absolute())


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
    aggregator = Aggregator(DATASOURCE, pc)
    aggregator.update_data()
    assert len(aggregator.data) == infos['plots']
    assert aggregator.ncols * aggregator.nrows == infos['plots']


@CONFIG_ROTATE
def test_viz(config, infos):
    pc = VizConfig.from_dict(config)
    plotter = Plotter(DATASOURCE, pc)
    plotter.create_viz()
    grid = plotter.get_output()

    save(grid, TEMP_FOLDER / f"{infos['name']}.html")

    assert True