from itertools import chain

from bokeh.models import HoverTool, GlyphRenderer

from pylow.data_preparation.plotinfo import PlotInfo


def generate_tooltip(renderer: GlyphRenderer, plot_info: PlotInfo) -> HoverTool:
    """ Creates and returns the tooltip-template for this plot"""
    # TODO FIXME: Figure out how to approach this, currently basically only a tech demo
    # TODO FIXME: need to hover it upwards of the point, otherwise it's shadowed by plots further down
    x_colname = plot_info.x_coords[0].attr.col_name if len(plot_info.x_coords) > 0 else ''  # FIXME #25
    y_colname = plot_info.y_coords[0].attr.col_name if len(plot_info.y_coords) > 0 else ''  # FIXME #25

    other_attributes = chain(plot_info.x_seps, plot_info.y_seps)
    additional = set(f'{avp.attr.col_name}: {avp.val}' for avp in other_attributes)

    tooltip = f"""
    <div>
        <span style="font-size: 15px;">{x_colname}: @{x_colname}</span><br>
        <span style="font-size: 15px;">{y_colname}: @{y_colname}</span>
    </div>
    <div>
        <span style="font-size: 10px;">{'<br>'.join(additional)}</span><br>
        <span style="font-size: 15px;">Size: @_size</span><br>
        <span style="font-size: 15px;">Color: @_color</span>

    </div>
    """
    return HoverTool(tooltips=tooltip, anchor='top_center', renderers=[renderer])
