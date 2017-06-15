from typing import List, Any

from pylow.data.attributes import Measure, Dimension
from pylow.data_preparation.avp import AVP
from pylow.data_preparation.colorizer import DEFAULT_COLOR, ALL_COLORS, adjust_brightness, \
    get_colors_for_color_separators
from pylow.utils import reverse_lerp


class ColorizationBehaviour:
    """ Base class for Colorization Behaviour, not useful to instantiate.
    """

    def __init__(self, vizconfig: 'VizConfig') -> None:
        self.vizconfig = vizconfig

    @staticmethod
    def get_correct_behaviour(vizconfig: 'VizConfig') -> 'ColorizationBehaviour':
        """ Dynamic dispatch behvaiour getter

        This is an implementation of the strategy pattern to encapsulate different types of colorization
        behaviour. Depending on the type of color (dimension, measure; in plot, not in plot; not existing)
        given in the config, this will select the correct strategy
        """

        color = vizconfig.color
        if color is None:
            return NoColorColorizationBehaviour(vizconfig)

        elif isinstance(color, Dimension):
            if color in vizconfig.columns_and_rows:
                return ExistingDimensionColorizationBehaviour(vizconfig)
            else:
                return NewDimensionColorizationBehaviour(vizconfig)

        # for measures, it makes no difference whether it's a new or existing attribute
        elif isinstance(color, Measure):
            return MeasureColorizationBehaviour(vizconfig)

        else:
            assert False

    def get_colors(self, plot_info: 'PlotInfo') -> List['AVP']:
        raise NotImplementedError('get_colors() is only available in subclasses of ColorizationBehaviour')


class NoColorColorizationBehaviour(ColorizationBehaviour):
    """ Colorization strategy for cases where no color at all is supplied in the configuration
    """

    def get_colors(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Will return a list of default colors matching the amount of glyphs
        """
        return [AVP('Default Color', DEFAULT_COLOR)] * len(plot_info.x_coords)


class ExistingDimensionColorizationBehaviour(ColorizationBehaviour):
    def get_colors(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Find all possible values that are in any plot of the screen
        """
        # TODO FIXME currently only finds the possible values in THIS plot!
        conf_color = self.vizconfig.color
        possible_vals = sorted(set(plot_info.variations_of(conf_color)))
        attribute_vals = [avp.val for avp in plot_info.find_attributes(conf_color)]
        # create a avp with (Attribute, hex_of_color) for each value
        avps = [AVP(conf_color, ALL_COLORS[possible_vals.index(curr_val)]) for curr_val in attribute_vals]
        return avps


class NewDimensionColorizationBehaviour(ColorizationBehaviour):
    def get_colors(self, plot_info: 'PlotInfo') -> List['AVP']:
        color_data = plot_info.additional_data
        # TODO FIXME: This is ALL extra data, need to handle cases where more of those appear
        assert len(color_data) == len(plot_info.x_coords)
        return list(get_colors_for_color_separators(color_data))


class MeasureColorizationBehaviour(ColorizationBehaviour):
    def get_colors(self, plot_info: 'PlotInfo') -> List['AVP']:
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
