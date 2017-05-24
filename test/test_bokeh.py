import os
import pathlib
import sys
from time import sleep

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pylow  # noqa
import pytest



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

CONF_2d0m_1d1m = {
    'columns': [pylow.Dimension('Category'), pylow.Dimension('Region')],
    'rows': [pylow.Dimension('Ship Mode'), pylow.Measure('Quantity')]
}

CONFIG_ROTATE = pytest.mark.parametrize("config,dimensions,measures", [
    # (CONF_1d0m_0d1m, 1, 1),
    # (CONF_0d1m_1d0m, 1, 1),
    # (CONF_2d0m_0d1m, 2, 1),
    (CONF_2d0m_1d1m, 3, 1),
])


@CONFIG_ROTATE
def test_config_builder(config, dimensions, measures):
    pc = pylow.VizConfig.from_dict(config)
    assert len(pc.dimensions) == dimensions
    assert len(pc.measures) == measures


def test_output_ordering():
    pc = pylow.VizConfig.from_dict(CONF_2d0m_1d1m)
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

@CONFIG_ROTATE
def test_example(config, dimensions, measures):
    pc = pylow.VizConfig.from_dict(config)
    ds = pylow.Datasource.from_csv(TEST_FILE.absolute())
    plotter = pylow.BokehPlotter(ds, pc)
    plotter.create_viz()
    plotter.display()
    sleep(0.5)  # make sure the browser has time to render the temp file
    assert True


if __name__ == '__main__':
    pytest.main(['-s'])
