import re
from collections import defaultdict
from functools import reduce
from itertools import product
from typing import Generator, List, Tuple, Dict, Any, Union, Iterable

import pytest

from pylow.data.attributes import Dimension, Measure, Attribute
from pylow.data.vizconfig import VizConfig
from pylow.utils import MarkType
from .testutils import DATASOURCE

ConfigInfo = Dict[str, Any]
Config = Tuple[VizConfig, ConfigInfo]
ConfigAttribute = Union[List[Attribute], MarkType]


def get_configs(filtering=None) -> List[Config]:
    all_configs = list(_build_configs())
    if filtering is not None:
        def filter_func(vc: Config) -> bool:
            return bool(re.search(filtering, str(vc[0])))

        all_configs = list(filter(filter_func, all_configs))

    return list(all_configs)


def _build_configs() -> Generator[Config, None, None]:
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
    relevant_attributes = {color, size}
    if len(vizconfig.columns) > 0:
        relevant_attributes.add(vizconfig.last_column)
    if len(vizconfig.rows) > 0:
        relevant_attributes.add(vizconfig.last_row)
    relevant_dimensions: List[Dimension] = VizConfig.find_attrs(relevant_attributes, Dimension)
    variations = [DATASOURCE.get_variations_of(d) for d in relevant_dimensions]
    glyph_amount = reduce(lambda old, new: old * new, map(len, variations), 1)
    return glyph_amount


def _determine_plot_amount(vizconfig: VizConfig) -> int:
    """ Determine how many single plots there will be in a visualization

    Works by multiplying the length of all not-last-in-plot dimensions in columns and rows
    """

    relevant_attributes = vizconfig.previous_columns + vizconfig.previous_rows
    relevant_dimensions: List[Dimension] = VizConfig.find_attrs(relevant_attributes, Dimension)
    variations = [DATASOURCE.get_variations_of(d) for d in relevant_dimensions]
    plot_amount = reduce(lambda old, new: old * new, map(len, variations), 1)
    return plot_amount


def _build_config_dicts() -> Generator[Dict[str, List[List[ConfigAttribute]]], None, None]:
    """ Goes through all possible combinations of configuration options and returns them all
    """
    attribute_order, permutations = _get_possible_permutations()
    for permuation in permutations:
        config_dict: Dict[str, List[ConfigAttribute]] = defaultdict(list)
        for attr, options in zip(attribute_order, permuation):
            if attr in ('columns', 'rows'):
                config_dict[attr] += options  # type: ignore
            else:
                config_dict[attr] = options  # type: ignore
        yield dict(config_dict)  # type: ignore


def _get_possible_permutations() -> Tuple[List[str], List[Iterable[ConfigAttribute]]]:
    """ Contains the lists of possible options for a plot and combines them in all possible ways
    """
    col_dim_combs = [[], [Dimension('Category')], [Dimension('Category'), Dimension('Region')]]
    row_dim_combs = [[], [Dimension('Ship Mode')]]
    col_measure_combs: List[List[Attribute]] = [[]]
    row_measure_combs = [[Measure('Quantity')]]
    colors = [None, Dimension('Region'), Measure('Quantity'), Dimension('State'), Measure('Profit')]
    sizes = [None, Dimension('Region'), Measure('Quantity'), Dimension('Segment'), Measure('Profit')]
    marks = [MarkType.CIRCLE]

    # generate permutations
    attribute_order = ['columns', 'rows', 'columns', 'rows', 'color', 'size', 'mark_type']
    segments = [col_dim_combs, row_dim_combs, col_measure_combs, row_measure_combs, colors, sizes, marks]
    permuations = product(*segments)  # type:ignore
    return attribute_order, list(permuations)


# Use regex to limit testing to the configurations currently relevant while developing
# TODO can we make this depend on a pytest argument? then we could set up CI to test more specific stuff
configs = get_configs()

# Pytest parameterized decorator to iterate over all possible configurations in testing
# This object is the main export of this test class and used in other testing code
CONFIG_ROTATE = pytest.mark.parametrize("viz_config,infos", list(configs))
