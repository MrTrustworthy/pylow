import json

from bs4 import BeautifulSoup

from pylow.data import VizConfig
from pylow.data_preparation import Aggregator
from pylow.plotting import Plotter
from .config_builder import CONFIG_ROTATE
from .testutils import DATASOURCE, save_plot_temp, get_plot_temp


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
    check_html(infos)


def check_html(infos):
    file_name = get_plot_temp(infos['name'])
    json_plot = extract_plot_structure(file_name)
    assert json_plot is not None
    roots_title_version = json_plot[list(json_plot.keys())[0]]
    roots = roots_title_version['roots']
    references = roots['references']  # type: list
    # has attributes, id and type; attributes has plot, x, y, text, ...

    # check for plot amounts
    plots = [ref for ref in references if ref['type'] == 'Plot']
    glyphs = [ref for ref in references if ref['type'] == 'Circle']  # FIXME dynamic glyph selection
    renderers = [ref for ref in references if ref['type'] == 'GlyphRenderer']
    assert len(plots) == len(renderers) == len(glyphs) == infos['plots']

    column_datasources = [ref for ref in references if ref['type'] == 'ColumnDataSource']
    data = [ref['attributes']['data'] for ref in column_datasources]

    # check for colors
    all_colors = sum([d['_color'] for d in data], [])
    if 'colN' in infos['name']:
        assert len(set(all_colors)) == 1
    else:
        assert len(set(all_colors)) > 1


def extract_plot_structure(file_name: str) -> json:
    with open(file_name) as infile:
        soup = BeautifulSoup(infile, 'html.parser')

    assert soup is not None

    scripts = soup.find_all('script')
    relevant_script = [s for s in scripts if 'docs_json =' in s.text][0]
    string = relevant_script.text.split('docs_json =')[-1]
    string = string.split('var render_items =')[0]
    string = string.replace(';', '')  # FIXME better splitting?
    json_plot = json.loads(string)
    return json_plot
