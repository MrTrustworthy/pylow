
from bokeh.core.properties import String, Instance
from bokeh.models import Line



class FlexLine(Line):

    __implementation__ = 'flexline.coffee'
