from bokeh.core.properties import field
from bokeh.models import Glyph, VBar, Circle

from datapylot.extensions.flexline import FlexLine
from datapylot.utils import MarkType, ColumnNameCollection


def create_glyph(mark_type: MarkType, col_names: ColumnNameCollection) -> Glyph:
    """ Creates a glyph based on the configuration"""
    _mark_to_glyph = {
        MarkType.LINE: _make_line,
        MarkType.BAR: _make_bar,
        MarkType.CIRCLE: _make_circle
    }
    return _mark_to_glyph[mark_type](col_names)


def _make_line(col_names: ColumnNameCollection) -> Glyph:
    return FlexLine(
        x=field(col_names.x),
        y=field(col_names.y),
        size=field(col_names.size),
        colors=field(col_names.color)
    )


def _make_bar(col_names: ColumnNameCollection) -> Glyph:
    return VBar(
        x=field(col_names.x),
        top=field(col_names.y),
        fill_color=field(col_names.color),
        line_color=field(col_names.color),
        width=field(col_names.size)
    )


def _make_circle(col_names: ColumnNameCollection) -> Glyph:
    return Circle(
        x=field(col_names.x),
        y=field(col_names.y),
        fill_color=field(col_names.color),
        line_color=field(col_names.color),
        size=field(col_names.size)
    )
