import {div, empty} from "core/dom"

# The "core/properties" module has all the property types
import * as p from "core/properties"

# We will subclass in JavaScript from the same class that was subclassed
# from in Python
import {XYGlyph, XYGlyphView} from "models/glyphs/xy_glyph"


# This model will actually need to render things, so we must provide
# view. The LayoutDOM model has a view already, so we will start with that
export class FlexLineView extends XYGlyphView

  initialize: (options) ->
    super(options)


  render: (ctx, indices, {sx, sy, _size, _colors}) ->
    @visuals.fill.set_value(ctx)
    pointsOneway = indices.length

    # TODO flip color axis based on optional parameter 'flipped'
    # make the color a gradient
    gradient = ctx.createLinearGradient(sx[0], 0, sx[pointsOneway-1], 0)
    for color, i in _colors
      position = i / (_colors.length - 1)
      gradient.addColorStop(position, color)
    ctx.fillStyle = gradient

    # line must go one way & back
    allPointIndicies = [0..pointsOneway - 1].concat [pointsOneway - 1..0]

    # for each point, have two Y values (line forwards & line backwards)
    isOnFirstWay = true
    for i in allPointIndicies
      sxVal = sx[i]
      # TODO flip width to apply to X-axis for flipped lines
      syVal = sy[i] + (if isOnFirstWay then _size[i] else - _size[i])

      if i == 0 and isOnFirstWay
        ctx.beginPath()
        ctx.moveTo(sxVal, syVal)
      else
        ctx.lineTo(sxVal, syVal)

      # flip orientation once we have reached the end of the 1st line
      if i == pointsOneway - 1
        isOnFirstWay = false

    ctx.closePath()
    ctx.fill()

export class FlexLine extends XYGlyph

  # If there is an associated view, this is boilerplate.
  default_view: FlexLineView

  # The ``type`` class attribute should generally match exactly the name
  # of the corresponding Python class.
  type: "FlexLine"
  @mixins ['line', 'fill']

  # The @define block adds corresponding "properties" to the JS model. These
  # should basically line up 1-1 with the Python model class. Most property
  # types have counterparts, e.g. bokeh.core.properties.String will be
  # p.String in the JS implementation. Where the JS type system is not yet
  # as rich, you can use p.Any as a "wildcard" property type.
  @define {
    sx: [p.NumberSpec]
    sy: [p.NumberSpec]
    size: [p.NumberSpec]
    colors: [p.ColorSpec]
  }
