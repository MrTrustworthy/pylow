from collections import defaultdict
from itertools import product
from typing import Generator, List, Tuple

import pytest

from pylow.data.attributes import Dimension, Measure, Attribute
from pylow.data.vizconfig import VizConfig
from pylow.utils import MarkType


def build_configs() -> Generator[VizConfig, None, None]:
    """ Dynamically create a set of VizConfig's for testing
    """
    for conf_dict in _build_config_dicts():
        # TODO add automatic calculating of the plot amount by generating a datasource
        info = {'plot_amount': 12}
        yield VizConfig.from_dict(conf_dict), info


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
    col_dim_combs = [[Dimension('Category'), Dimension('Region')]]
    row_dim_combs = [[Dimension('Ship Mode')]]
    col_measure_combs = [[]]
    row_measure_combs = [[Measure('Quantity')]]
    colors = [None]  # , Dimension('Region'), Measure('Quantity'), Dimension('State'), Measure('Profit')]
    sizes = [None, Dimension('Region'), Measure('Quantity'), Dimension('State'), Measure('Profit')]
    marks = [MarkType.CIRCLE]

    # generate permutations
    attribute_order = ['columns', 'rows', 'columns', 'rows', 'color', 'size', 'mark_type']
    permuations = product(col_dim_combs, row_dim_combs, col_measure_combs, row_measure_combs, colors, sizes, marks)
    return attribute_order, permuations


# Pytest parameterized decorator to iterate over all possible configurations in testing
CONFIG_ROTATE = pytest.mark.parametrize("viz_config,infos", list(build_configs()))
