import json
from typing import List

from bs4 import BeautifulSoup

from datapylot.data.vizconfig import NoSuchAttributeException
from datapylot.data_preparation.aggregator import Aggregator
from datapylot.plotting import Plotter
from .config_builder import CONFIG_ROTATE
from .testutils import DATASOURCE, save_plot_temp, get_plot_temp


@CONFIG_ROTATE
def test_aggregator(viz_config, infos):
    aggregator = Aggregator(DATASOURCE, viz_config)
    aggregator.update_data()
    assert len(aggregator.data) == aggregator.ncols * aggregator.nrows == infos['plot_amount']


@CONFIG_ROTATE
def test_viz(viz_config, infos) -> None:
    plotter = Plotter(DATASOURCE, viz_config)
    plotter.create_viz()
    grid = plotter.get_output()
    save_plot_temp(grid, str(viz_config))
    check_html(viz_config, infos)


def check_html(viz_config, infos) -> None:
    file_name = get_plot_temp(str(viz_config))
    json_plot = extract_plot_structure(file_name)

    assert json_plot is not None

    # parse the json plot
    roots_title_version = json_plot[list(json_plot.keys())[0]]
    roots = roots_title_version['roots']
    references = roots['references']  # type: list
    # has attributes, id and type; attributes has plot, x, y, text, ...

    # check for plot amounts
    plots = [ref for ref in references if ref['type'] == 'Plot']
    glyphs = [ref for ref in references if ref['type'] == viz_config.mark_type.value.glyph_name]
    renderers = [ref for ref in references if ref['type'] == 'GlyphRenderer']
    if not (len(plots) == len(renderers) == len(glyphs) == infos['plot_amount']):
        import pdb; pdb.set_trace()

    column_datasources = [ref for ref in references if ref['type'] == 'ColumnDataSource']
    data = [ref['attributes']['data'] for ref in column_datasources]

    # check for colors
    all_colors: List[str] = sum([d['_color'] for d in data], [])  # type: ignore
    if 'colN' in str(viz_config):
        assert len(set(all_colors)) == 1
    else:
        assert len(set(all_colors)) >= 1

    # check for sizes
    all_sizes: List[int] = sum([d['_size'] for d in data], [])  # type: ignore
    if 'sizeN' in str(viz_config):
        assert len(set(all_sizes)) == 1
    else:
        assert len(set(all_sizes)) >= 1

    # check for glyph amounts
    colname: str = ''
    try:
        colname = viz_config.x_data.col_name
    except NoSuchAttributeException:
        pass
    glyph_amounts = [len(d[colname]) for d in data]
    # since not all plots will contain all dimension values, the glyph amount can be less than the max amount
    assert max(glyph_amounts) <= infos['glyphs_in_plot_amount']


def extract_plot_structure(file_name: str) -> dict:
    with open(file_name) as infile:
        soup = BeautifulSoup(infile, 'html.parser')

    assert soup is not None

    scripts = soup.find_all('script')
    relevant_script = [s for s in scripts if 'docs_json =' in s.text][0]
    # scrape the relevant JSON fragment from the script text
    string = relevant_script.text.split('docs_json =')[-1]
    string = string.split('var render_items =')[0]
    string = string.replace(';', '')  # FIXME better splitting?
    json_plot = json.loads(string)
    return json_plot
