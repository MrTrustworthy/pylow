import {div, empty} from "core/dom"

# The "core/properties" module has all the property types
import * as p from "core/properties"

# We will subclass in JavaScript from the same class that was subclassed
# from in Python
import {Patch, PatchView} from "models/glyphs/patch"

# This model will actually need to render things, so we must provide
# view. The LayoutDOM model has a view already, so we will start with that
export class FlexLineView extends PatchView

  initialize: (options) ->
    # Object {model: FlexLine, renderer: e, plot_view: e}
    super(options)

    # @render()

    # Set Backbone listener so that when the Bokeh slider has a change
    # event, we can process the new data
    # @listenTo(@model.slider, 'change', () => @render())

  render: (ctx, indices, {sx, sy, _line_width}) ->
    if @visuals.line.doit
      # @visuals.line.set_value(ctx) need to set manually

      pointsOneway = indices.length
      totalPoints = pointsOneway * 2
      indicies = [0..pointsOneway - 1].concat [pointsOneway - 1..0]

      isOnFirstWay = true
      for i in indicies
        debugger
        sxVal = sx[i]
        syVal = sy[i] + (if isOnFirstWay then _line_width[i] else - _line_width[i])

        if i == 0 and isOnFirstWay
          ctx.beginPath()
          ctx.moveTo(sxVal, syVal)
        else
          ctx.lineTo(sxVal, syVal)

        if i == pointsOneway - 1
          isOnFirstWay = false

      ctx.closePath()
      ctx.stroke()

export class FlexLine extends Patch

  # If there is an associated view, this is boilerplate.
  default_view: FlexLineView

  # The ``type`` class attribute should generally match exactly the name
  # of the corresponding Python class.
  type: "FlexLine"

  # The @define block adds corresponding "properties" to the JS model. These
  # should basically line up 1-1 with the Python model class. Most property
  # types have counterparts, e.g. bokeh.core.properties.String will be
  # p.String in the JS implementation. Where the JS type system is not yet
  # as rich, you can use p.Any as a "wildcard" property type.
  # @define {
  #   text:   [ p.String ]
  #   slider: [ p.Any    ]
  # }
