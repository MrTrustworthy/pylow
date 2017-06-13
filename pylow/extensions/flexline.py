from bokeh.core.properties import NumberSpec, ColorSpec
from bokeh.models import Glyph


class FlexLine(Glyph):
    __implementation__ = 'flexline.coffee'

    x = NumberSpec()
    y = NumberSpec()
    size = NumberSpec(default=10)
    colors = ColorSpec(default='black')
