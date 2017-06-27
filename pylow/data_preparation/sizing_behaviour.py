from itertools import chain
from typing import List, Any, Union

from pylow.data.attributes import Measure, Dimension
from pylow.data_preparation.avp import AVP
from pylow.utils import reverse_lerp

Number = Union[int, float]


class SizingBehaviour:
    """ Base class for Sizing Behaviour, not useful to instantiate.
    """

    def __init__(self, vizconfig: 'VizConfig', all_plotinfos: List['PlotInfo']) -> None:
        self.vizconfig = vizconfig
        # needed in order to find the min/max ranges for measures and provide consistent sizes for dimensions
        self.all_plotinfos = all_plotinfos

    @staticmethod
    def get_correct_behaviour(vizconfig: 'VizConfig', all_plotinfos: List['PlotInfo']) -> 'SizingBehaviour':
        """ Basically a dynamic dispatch behvaiour getter

        This is an implementation of the strategy pattern to encapsulate different types of sizeization
        behaviour. Depending on the type of size (dimension, measure; in plot, not in plot; not existing)
        given in the config, this will select the correct strategy
        """

        size = vizconfig.size
        if size is None:
            return NoColorSizingBehaviour(vizconfig, all_plotinfos)

        # there is only one sizing behaviour for dimensions:
        # if size is an already existing dimension, it will work straight forward and size every glyph
        # if size is a new dimension, the aggregation will additionally split the data into (much) more glyphs
        elif isinstance(size, Dimension):
            return DimensionSizingBehaviour(vizconfig, all_plotinfos)
        # for measures, it makes no difference whether it's a new or existing attribute
        # sizeization is based on the min-max range then
        elif isinstance(size, Measure):
            return MeasureSizingBehaviour(vizconfig, all_plotinfos)

        else:
            assert False

    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Will raise NotImplementedError to remind you to overwrite it in subclasses
        """
        raise NotImplementedError('get_sizes() is only available in subclasses of SizingBehaviour')


class NoColorSizingBehaviour(SizingBehaviour):
    """ Sizing strategy for cases where no size at all is supplied in the configuration
    """

    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Will return a list of default sizes matching the amount of glyphs
        """
        # for 0d0m-configurations, the lengths of axes might differ
        longest_axes = max(len(plot_info.x_coords), len(plot_info.y_coords))
        return [AVP('Default Size', self.vizconfig.mark_type.value.glyph_size_factor)] * longest_axes


class DimensionSizingBehaviour(SizingBehaviour):
    """ If the size is an already existing dimension, it will work straight forward and size every glyph
    """

    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Find all possible values that are in any plot of the screen
        """
        # find the variations of the dimensions value
        conf_size = self.vizconfig.size
        base_size = self.vizconfig.mark_type.value.glyph_size_factor

        # find all variations
        variations = [pi.variations_of(conf_size) for pi in self.all_plotinfos]
        possible_vals = sorted(set(chain(*variations)))

        attribute_vals = [avp.val for avp in plot_info.find_attributes(conf_size)]

        # create a avp with (Attribute, size) for each value
        get_size = self._get_size_for_dimension
        sizes = [get_size(curr_val, possible_vals, base_size) for curr_val in attribute_vals]

        avps = [AVP(conf_size, size) for size in sizes]
        return avps

    @staticmethod
    def _get_size_for_dimension(value: Number, all_values: List[Number], base_size: Number) -> Number:
        index = all_values.index(value)
        indicie_range = len(all_values) - 1
        assert index > -1
        zero_position = -1 * (indicie_range / 2)
        current_position = zero_position + index  # can range from -(indicie_range/2) to (indicie_range/2)
        scaling_factor_per_step = base_size / indicie_range
        current_size = base_size + (current_position * scaling_factor_per_step)
        return current_size


class MeasureSizingBehaviour(SizingBehaviour):
    """ For measures, sizing is based on min-max lerping of a size

    In those cases, it doesn't make a difference if the measure is already somewhere else on the plot.
    """

    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Find all possible values that are in any plot of the screen
        """
        # FIXME Not yet working for MX-Configs!
        conf_size = self.vizconfig.size
        variations = [pi.variations_of(conf_size) for pi in self.all_plotinfos]
        possible_vals = sorted(set(chain(*variations)))
        attribute_vals = [avp.val for avp in plot_info.find_attributes(conf_size)]
        # create a avp with (Attribute, hex_of_size) for each value
        avps = [self._get_size_data(curr_val, possible_vals) for curr_val in attribute_vals]
        return avps

    def _get_size_data(self, curr_val: Any, possible_vals: List[Any]) -> AVP:
        """ Reverse-lerp's a size value based on the possible values
        """
        relative_in_range = reverse_lerp(curr_val, possible_vals)  # between 0 and 1
        assert 0.0 <= relative_in_range <= 1.0
        scale_factor = relative_in_range + 0.5  # Turn into range (0.5, 1.5)
        size = self.vizconfig.mark_type.value.glyph_size_factor * scale_factor
        size_avp = AVP(self.vizconfig.size, size)
        return size_avp
