import re
from collections import defaultdict
from functools import reduce
from itertools import product
from typing import Generator, List, Tuple

import pytest

from pylow.data.attributes import Dimension, Measure, Attribute
from pylow.data.vizconfig import VizConfig
from pylow.utils import MarkType
from .testutils import DATASOURCE


def get_configs(filtering=None):
    all_configs = _build_configs()
    if filtering is not None:
        all_configs = filter(lambda vc: re.search(filtering, str(vc[0])), all_configs)

    return all_configs


def _build_configs() -> Generator[VizConfig, None, None]:
    """ Dynamically create a set of VizConfig's for testing
    """
    for conf_dict in _build_config_dicts():
        # TODO add automatic calculating of the plot amount by generating a datasource
        info = {}
        vizconfig = VizConfig.from_dict(conf_dict)
        info['plot_amount'] = _determine_plot_amount(vizconfig)
        info['glyphs_in_plot_amount'] = _determine_glyphs_in_plot_amount(vizconfig)
        yield vizconfig, info


def _determine_glyphs_in_plot_amount(vizconfig: VizConfig) -> int:
    """ Determine how many glyphs will be in a single plot

    Works by multiplying the length of all not-last-in-plot dimensions in columns and rows
    """
    color = vizconfig.color if vizconfig.color not in vizconfig.columns_and_rows else None
    size = vizconfig.size if vizconfig.size not in vizconfig.columns_and_rows else None

    relevant_attributes = {vizconfig.last_column, vizconfig.last_row, color, size}
    relevant_dimensions = VizConfig.find_attrs(relevant_attributes, Dimension)
    variations = [DATASOURCE.get_variations_of(d) for d in relevant_dimensions]
    glyph_amount = reduce(lambda old, new: old * new, map(len, variations), 1)
    return glyph_amount


def _determine_plot_amount(vizconfig: VizConfig) -> int:
    """ Determine how many single plots there will be in a visualization

    Works by multiplying the length of all not-last-in-plot dimensions in columns and rows
    """
    relevant_attributes = vizconfig.previous_columns + vizconfig.previous_rows
    relevant_dimensions = VizConfig.find_attrs(relevant_attributes, Dimension)
    variations = [DATASOURCE.get_variations_of(d) for d in relevant_dimensions]
    plot_amount = reduce(lambda old, new: old * new, map(len, variations), 1)
    return plot_amount


def _build_config_dicts() -> Generator[dict, None, None]:
    attribute_order, permutations = _get_possible_permutations()
    for permuation in permutations:
        config_dict = defaultdict(list)
        for attr, options in zip(attribute_order, permuation):
            if attr in 'columns' or attr in 'rows':
                config_dict[attr] += options
            else:
                config_dict[attr] = options
        yield dict(config_dict)


def _get_possible_permutations() -> Tuple[List[str], List[List[Attribute]]]:
    col_dim_combs = [[Dimension('Category')], [Dimension('Category'), Dimension('Region')]]
    row_dim_combs = [[Dimension('Ship Mode')]]
    col_measure_combs = [[]]
    row_measure_combs = [[Measure('Quantity')]]
    colors = [None, Dimension('Region'), Measure('Quantity'), Dimension('State'), Measure('Profit')]
    sizes = [None, Dimension('Region'), Measure('Quantity'), Dimension('Segment'), Measure('Profit')]
    marks = [MarkType.CIRCLE]

    # generate permutations
    attribute_order = ['columns', 'rows', 'columns', 'rows', 'color', 'size', 'mark_type']
    permuations = product(col_dim_combs, row_dim_combs, col_measure_combs, row_measure_combs, colors, sizes, marks)
    return attribute_order, permuations


# Use regex to limit testing to the configurations currently relevant while developing
configs = get_configs(r'\dd0m_1d1m_sizeN._colN.')

# Pytest parameterized decorator to iterate over all possible configurations in testing
CONFIG_ROTATE = pytest.mark.parametrize("viz_config,infos", list(configs))
