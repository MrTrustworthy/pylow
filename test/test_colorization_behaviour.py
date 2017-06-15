from pylow.data.attributes import Dimension, Measure
from pylow.data.vizconfig import VizConfig
from pylow.data_preparation.colorization_behaviour import *


def test_colorization_behaviour_selection():
    no_color = {
        'columns': [],
        'rows': [],
    }
    d_existing_color = {
        'columns': [Dimension('Region')],
        'rows': [],
        'color': Dimension('Region'),
    }
    m_existing_color = {
        'columns': [Measure('Quantity')],
        'rows': [],
        'color': Measure('Quantity')
    }

    d_non_existing_color = {
        'columns': [],
        'rows': [],
        'color': Dimension('State')
    }
    m_non_existing_color = {
        'columns': [],
        'rows': [],
        'color': Measure('Profit')
    }

    configs = [no_color, d_existing_color, m_existing_color, d_non_existing_color, m_non_existing_color]
    vizconfigs = [VizConfig.from_dict(d) for d in configs]
    classes = [NoColorColorizationBehaviour, ExistingDimensionColorizationBehaviour,
               MeasureColorizationBehaviour, NewDimensionColorizationBehaviour, MeasureColorizationBehaviour]

    # check that the colorization behaviour dispatch returns the correct classes
    for conf, _class in zip(vizconfigs, classes):
        behaviour = ColorizationBehaviour.get_correct_behaviour(conf)
        assert isinstance(behaviour, _class)
