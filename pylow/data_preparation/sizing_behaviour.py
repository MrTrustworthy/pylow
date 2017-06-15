from itertools import chain, cycle
from typing import List, Any, Generator

from pylow.data.attributes import Measure, Dimension
from pylow.data_preparation.avp import AVP
from pylow.utils import reverse_lerp


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

        # there are two sizeization behaviours for dimensions:
        # if size is an already existing dimension, it will work straight forward and size every glyph
        # if size is a new dimension, the aggregation will additionally split the data into (much) more glyphs
        elif isinstance(size, Dimension):
            if size in vizconfig.columns_and_rows:
                return ExistingDimensionSizingBehaviour(vizconfig, all_plotinfos)
            else:
                return NewDimensionSizingBehaviour(vizconfig, all_plotinfos)

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
        return [AVP('Default Size', self.vizconfig.mark_type.value.glyph_size_factor)] * len(plot_info.x_coords)


class ExistingDimensionSizingBehaviour(SizingBehaviour):
    """ If the size is an already existing dimension, it will work straight forward and size every glyph
    """

    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Find all possible values that are in any plot of the screen
        """
        # find the variations of the dimensions value
        conf_size = self.vizconfig.size

        variations = [pi.variations_of(conf_size) for pi in self.all_plotinfos]
        possible_vals = sorted(set(chain(*variations)))
        attribute_vals = [avp.val for avp in plot_info.find_attributes(conf_size)]

        # create a avp with (Attribute, hex_of_size) for each value
        avps = [AVP(conf_size, self._get_size_for_value(curr_val, possible_vals)) for curr_val in attribute_vals]
        return avps

    def _get_size_for_value(self, value, all_values):
        default_size = self.vizconfig.mark_type.value.glyph_size_factor
        index = all_values.index(value)
        indicie_range = len(all_values) - 1
        assert index > -1
        zero_index = indicie_range / 2
        current_position = zero_index - index
        scaling_factor_per_step = default_size / indicie_range
        current_size = default_size + (current_position * scaling_factor_per_step)
        return current_size


class NewDimensionSizingBehaviour(SizingBehaviour):
    """ If the size is a new dimension, the aggregation will additionally split the data into (much) more glyphs

    This strategy class will deal wit hthose cases
    """

    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        size_data = plot_info.additional_data
        # TODO FIXME: This is ALL extra data, need to handle cases where more of those appear
        # TODO FIXME: Need to consider ALL data in ALL plots here
        assert len(size_data) == len(plot_info.x_coords)
        return list(self.get_sizes_for_size_separators(size_data))

    @staticmethod
    def get_sizes_for_size_separators(sizes: List['AVP']) -> Generator[AVP, None, None]:
        all_values = set(avp.val for avp in sizes)
        # TODO FIXME this is just an example
        val_to_size = dict(zip(all_values, cycle([1, 2, 3, 4])))
        for avp in sizes:
            yield AVP(avp.attr, val_to_size[avp.val])


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
        # turn into value from 0.5 to 2
        size_factor = (relative_in_range + 0.5) * (4 / 3)
        size = self.vizconfig.mark_type.value.glyph_size_factor * size_factor
        size_avp = AVP(self.vizconfig.size, size)
        return size_avp
