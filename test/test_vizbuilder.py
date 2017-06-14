from pylow.data import VizConfig
from pylow.data_preparation import Aggregator
from pylow.plotting import Plotter
from .config_builder import CONFIG_ROTATE
from .testutils import DATASOURCE, save_plot_temp


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
    save_plot_temp(grid, infos['name'])
    assert True
