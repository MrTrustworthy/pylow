from typing import List, Any

from pylow.data.attributes import Measure, Dimension
from pylow.data_preparation.avp import AVP
from pylow.utils import reverse_lerp


class SizingBehaviour:
    """ Base class for Colorization Behaviour, not useful to instantiate.
    """

    def __init__(self, vizconfig: 'VizConfig') -> None:
        self.vizconfig = vizconfig

    @staticmethod
    def get_correct_behaviour(vizconfig: 'VizConfig') -> 'SizingBehaviour':
        """ Dynamic dispatch behvaiour getter

        This is an implementation of the strategy pattern to encapsulate different types of colorization
        behaviour. Depending on the type of color (dimension, measure; in plot, not in plot; not existing)
        given in the config, this will select the correct strategy
        """

        color = vizconfig.color
        if color is None:
            return NoColorSizingBehaviour(vizconfig)

        elif isinstance(color, Dimension):
            if color in vizconfig.columns_and_rows:
                return ExistingDimensionSizingBehaviour(vizconfig)
            else:
                return NewDimensionSizingBehaviour(vizconfig)

        # for measures, it makes no difference whether it's a new or existing attribute
        elif isinstance(color, Measure):
            return MeasureSizingBehaviour(vizconfig)

        else:
            assert False

    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        raise NotImplementedError('get_sizes() is only available in subclasses of SizingBehaviour')


class NoColorSizingBehaviour(SizingBehaviour):
    """ Colorization strategy for cases where no color at all is supplied in the configuration
    """

    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Will return a list of default colors matching the amount of glyphs
        """
        return [AVP('Default Color', DEFAULT_COLOR)] * len(plot_info.x_coords)


class ExistingDimensionSizingBehaviour(SizingBehaviour):
    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Find all possible values that are in any plot of the screen
        """
        # TODO FIXME currently only finds the possible values in THIS plot!
        conf_color = self.vizconfig.color
        possible_vals = sorted(set(plot_info.variations_of(conf_color)))
        attribute_vals = [avp.val for avp in plot_info.find_attributes(conf_color)]
        # create a avp with (Attribute, hex_of_color) for each value
        avps = [AVP(conf_color, ALL_COLORS[possible_vals.index(curr_val)]) for curr_val in attribute_vals]
        return avps


class NewDimensionSizingBehaviour(SizingBehaviour):
    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        color_data = plot_info.additional_data
        # TODO FIXME: This is ALL extra data, need to handle cases where more of those appear
        assert len(color_data) == len(plot_info.x_coords)
        return list(get_sizes_for_color_separators(color_data))


class MeasureSizingBehaviour(SizingBehaviour):
    def get_sizes(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Find all possible values that are in any plot of the screen
        """
        # TODO FIXME currently only finds the possible values in THIS plot! need to compare with all other plots
        conf_color = self.vizconfig.color
        val_variation_lists = plot_info.variations_of(conf_color)
        possible_vals = sorted(set(val_variation_lists))
        attribute_vals = [avp.val for avp in plot_info.find_attributes(conf_color)]
        # create a avp with (Attribute, hex_of_color) for each value
        avps = [self._get_color_data(curr_val, possible_vals) for curr_val in attribute_vals]
        return avps

    def _get_color_data(self, curr_val: Any, possible_vals: List[Any]) -> AVP:
        """ Reverse-lerp's a color value based on the possible values
        """
        relative_in_range = reverse_lerp(curr_val, possible_vals)  # between 0 and 1
        # turn into value from -0.5 and 0.5 with 0.5 for the smallest values
        color_saturation = (relative_in_range - 0.5) * -1
        color = adjust_brightness(DEFAULT_COLOR, color_saturation)
        color_avp = AVP(self.vizconfig.color, color)
        return color_avp


# def _get_size_data(self, current_val: Any, possible_vals: List[Any]) -> AVP:
#     if isinstance(self.config.size, Dimension):
#         # TODO FIXME currently, size only affects plot in one direction -> bigger, need to clamp this
#         size = possible_vals.index(current_val)
#         size_avp = AVP(self.config.size, (size + 1))
#         return size_avp
#     else:  # for measures
#         relative_in_range = reverse_lerp(current_val, possible_vals)  # between 0 and 1
#         # turn into value from 0.5 to 2
#         size_factor = (relative_in_range + 0.5) * (4/3)
#         size_avp = AVP(self.config.size, size_factor)
#         return size_avp
