import pytest

from pylow.data.attributes import Dimension, Measure
from pylow.utils import MarkType

# Format Column<x dimensions, y measures> Rows<x dimensions, y measures>
CONF_1d0m_0d1m = {
    'columns': [Dimension('Category')],
    'rows': [Measure('Number of records')]
}
CONF_0d1m_1d0m = {
    'columns': [Measure('Number of records')],
    'rows': [Dimension('Category')]
}
CONF_2d0m_0d1m = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Measure('Quantity')]
}

CONF_2d0m_1d1m_colN = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
}

CONF_2d0m_1d1m_colD = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
    'color': Dimension('Region')
}

CONF_2d0m_1d1m_colM = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
    'color': Measure('Quantity')
}

CONF_2d0m_1d1m_sizeN = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
}

CONF_2d0m_1d1m_sizeD = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
    'size': Dimension('Region')
}

CONF_2d0m_1d1m_sizeM = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
    'size': Measure('Quantity')
}

CONF_2d0m_1d1m_sizeM_colD_line = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
    'size': Measure('Quantity'),
    'color': Dimension('Region'),
    'mark_type': MarkType.LINE
}

CONF_2d0m_1d1m_sizeN_colN_circle = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
    'mark_type': MarkType.CIRCLE
}

CONF_2d0m_1d1m_sizeN_colD_circle = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
    'color': Dimension('Region'),
    'mark_type': MarkType.CIRCLE
}
CONF_2d0m_1d1m_sizeN_colM_circle = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
    'color': Measure('Quantity'),
    'mark_type': MarkType.CIRCLE
}

CONF_2d0m_1d1m_sizeN_colDX_circle = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
    'color': Dimension('State'),
    'mark_type': MarkType.CIRCLE
}
CONF_2d0m_1d1m_sizeN_colMX_circle = {
    'columns': [Dimension('Category'), Dimension('Region')],
    'rows': [Dimension('Ship Mode'), Measure('Quantity')],
    'color': Measure('Profit'),
    'mark_type': MarkType.CIRCLE
}

CONFIG_ROTATE = pytest.mark.parametrize("config,infos", [

    (CONF_2d0m_1d1m_sizeN_colN_circle,
     {'dimensions': 3, 'measures': 1, 'plots': 12, 'color': None, 'color_sep': None,
      'name': 'CONF_2d0m_1d1m_sizeN_colN_circle'}
     ),
    (CONF_2d0m_1d1m_sizeN_colD_circle,
     {'dimensions': 3, 'measures': 1, 'plots': 12, 'color': 1, 'color_sep': None,
      'name': 'CONF_2d0m_1d1m_sizeN_colD_circle'}
     ),
    (CONF_2d0m_1d1m_sizeN_colM_circle,
     {'dimensions': 3, 'measures': 1, 'plots': 12, 'color': 1, 'color_sep': None,
      'name': 'CONF_2d0m_1d1m_sizeN_colM_circle'}
     ),
    (CONF_2d0m_1d1m_sizeN_colDX_circle,
     {'dimensions': 4, 'measures': 1, 'plots': 12, 'color': None, 'color_sep': 1,
      'name': 'CONF_2d0m_1d1m_sizeN_colDX_circle'}
     ),
    (CONF_2d0m_1d1m_sizeN_colMX_circle,  # FIXME color looks weird, check it out!
     {'dimensions': 3, 'measures': 2, 'plots': 12, 'color': 1, 'color_sep': None,
      'name': 'CONF_2d0m_1d1m_sizeN_colMX_circle'}
     )
])
