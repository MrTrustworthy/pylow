import os
import pathlib
import sys
import pytest
from time import sleep
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pylow  # noqa


TESTDATA_PATH = pathlib.Path('test/data')  # as seen from project root
TEST_FILE = TESTDATA_PATH / 'testdata_min.csv'

# Format Column<x dimensions, y measures> Rows<x dimensions, y measures>
CONF_1d0m_0d1m = {
    'columns': [pylow.Dimension('Category')],
    'rows': [pylow.Measure('Number of records', draw_type='plot', color='red')]
}
CONF_0d1m_1d0m = {
    'columns': [pylow.Measure('Number of records', draw_type='plot', color='red')],
    'rows': [pylow.Dimension('Category')]
}
CONF_2d0m_1m0d = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Measure('Quantity', draw_type='plot', color='blue')]
}

CONFIG_ROTATE = pytest.mark.parametrize("config,dimensions,measures", [
    (CONF_1d0m_0d1m, 1, 1),
    (CONF_0d1m_1d0m, 1, 1),
    #(CONF_2d0m_1m0d, 2, 1),
    # (CONF_2_2, 2, 2),
])


@CONFIG_ROTATE
def test_config_builder(config, dimensions, measures):
    pc = pylow.PlotConfig.from_dict(config)
    assert len(pc.dimensions) == dimensions
    assert len(pc.measures) == measures

@CONFIG_ROTATE
def test_example(config, dimensions, measures):
    pc = pylow.PlotConfig.from_dict(config)
    ds = pylow.Datasource.from_csv(TEST_FILE.absolute())
    plotter = pylow.BokehPlotter(ds, pc)
    plotter.create_viz()
    plotter.display(export_file='test/data/temp/test_0_1', wait=True)
    sleep(0.5)  # make sure the browser has time to render the temp file
    assert True


if __name__ == '__main__':
    pytest.main(['-s'])
