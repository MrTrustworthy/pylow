from itertools import chain, cycle
from typing import List, Any, Generator, TYPE_CHECKING

from datapylot.data.attributes import Measure, Dimension
from datapylot.data_preparation.avp import AVP
from datapylot.data_preparation.colorizer import DEFAULT_COLOR, ALL_COLORS, adjust_brightness
from datapylot.utils import reverse_lerp

# static type analysis
if TYPE_CHECKING:
    from datapylot.data.vizconfig import VizConfig
    from datapylot.data_preparation.plotinfo import PlotInfo


class ColorizationBehaviour:
    """ Base class for Colorization Behaviour, not useful to instantiate.
    """

    def __init__(self, vizconfig: 'VizConfig', all_plotinfos: List['PlotInfo']) -> None:
        self.vizconfig = vizconfig
        # needed in order to find the min/max ranges for measures and provide consistent colors for dimensions
        self.all_plotinfos = all_plotinfos

    @staticmethod
    def get_correct_behaviour(vizconfig: 'VizConfig', all_plotinfos: List['PlotInfo']) -> 'ColorizationBehaviour':
        """ Basically a dynamic dispatch behvaiour getter

        This is an implementation of the strategy pattern to encapsulate different types of colorization
        behaviour. Depending on the type of color (dimension, measure; in plot, not in plot; not existing)
        given in the config, this will select the correct strategy
        """

        color = vizconfig.color
        if color is None:
            return NoColorColorizationBehaviour(vizconfig, all_plotinfos)

        # there are two colorization behaviours for dimensions:
        # if color is an already existing dimension, it will work straight forward and color every glyph
        # if color is a new dimension, the aggregation will additionally split the data into (much) more glyphs
        elif isinstance(color, Dimension):
            if color in vizconfig.columns or color in vizconfig.rows:
                return ExistingDimensionColorizationBehaviour(vizconfig, all_plotinfos)
            else:
                return NewDimensionColorizationBehaviour(vizconfig, all_plotinfos)

        # for measures, it makes no difference whether it's a new or existing attribute
        # colorization is based on the min-max range then
        elif isinstance(color, Measure):
            return MeasureColorizationBehaviour(vizconfig, all_plotinfos)

        else:
            assert False

    def get_colors(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Will raise NotImplementedError to remind you to overwrite it in subclasses
        """
        raise NotImplementedError('get_colors() is only available in subclasses of ColorizationBehaviour')

    def __repr__(self):
        return f'{type(self).__name__}'


class NoColorColorizationBehaviour(ColorizationBehaviour):
    """ Colorization strategy for cases where no color at all is supplied in the configuration
    """

    def get_colors(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Will return a list of default colors matching the amount of glyphs
        """
        # for 0d0m-configurations, the lengths of axes might differ
        longest_axes = max(len(plot_info.x_coords), len(plot_info.y_coords))
        return [AVP('Default Color', DEFAULT_COLOR)] * longest_axes


class ExistingDimensionColorizationBehaviour(ColorizationBehaviour):
    """ If the color is an already existing dimension, it will work straight forward and color every glyph
    """

    def get_colors(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Find all possible values that are in any plot of the screen
        """
        # find the variations of the dimensions value
        conf_color = self.vizconfig.color
        variations = [pi.variations_of(conf_color) for pi in self.all_plotinfos]
        possible_vals = sorted(set(chain(*variations)))
        attribute_vals = [avp.val for avp in plot_info.find_attributes(conf_color)]

        # if this dimension is a plot separator, there might only be one value -> extend the list to match the amount
        amount = len(plot_info.get_coord_values('x'))
        if len(attribute_vals) < amount:
            assert len(attribute_vals) == 1
            attribute_vals *= amount

        # create a avp with (Attribute, hex_of_color) for each value
        avps = [AVP(conf_color, ALL_COLORS[possible_vals.index(curr_val)]) for curr_val in attribute_vals]

        return avps


class NewDimensionColorizationBehaviour(ColorizationBehaviour):
    """ If the color is a new dimension, the aggregation will additionally split the data into (much) more glyphs

    This strategy class will deal wit hthose cases
    """

    def get_colors(self, plot_info: 'PlotInfo') -> List['AVP']:
        # TODO FIXME: Need to consider ALL data in ALL plots here
        # TODO FIXME: Do we need sorting here to ensure dimensions are colored the same?
        color_data = plot_info.find_attributes(self.vizconfig.color)
        assert len(color_data) == len(plot_info.get_coord_values('x'))
        return list(self.get_colors_for_color_separators(color_data))

    @staticmethod
    def get_colors_for_color_separators(col_seps: List['AVP']) -> Generator[AVP, None, None]:
        all_values = set(avp.val for avp in col_seps)
        val_to_color = dict(zip(all_values, cycle(ALL_COLORS)))
        for avp in col_seps:
            yield AVP(avp.attr, val_to_color[avp.val])


class MeasureColorizationBehaviour(ColorizationBehaviour):
    """ For measures, colorization is based on min-max lerping of a color

    In those cases, it doesn't make a difference if the measure is already somewhere else on the plot.
    """

    def get_colors(self, plot_info: 'PlotInfo') -> List['AVP']:
        """ Find all possible values that are in any plot of the screen
        """
        conf_color = self.vizconfig.color
        variations = [pi.variations_of(conf_color) for pi in self.all_plotinfos]
        possible_vals = sorted(set(chain(*variations)))
        # might have the same measure twice (1m/1m configs), so we need to filter that out
        attributes = list(plot_info.find_attributes(conf_color))  # TODO set?
        attribute_vals = [avp.val for avp in attributes]
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
