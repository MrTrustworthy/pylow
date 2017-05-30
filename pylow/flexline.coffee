import {div, empty} from "core/dom"

# The "core/properties" module has all the property types
import * as p from "core/properties"

# We will subclass in JavaScript from the same class that was subclassed
# from in Python
import {Line, LineView} from "models/glyphs/line"

# This model will actually need to render things, so we must provide
# view. The LayoutDOM model has a view already, so we will start with that
export class FlexLineView extends LineView

  initialize: (options) ->
    super(options)

    # @render()

    # Set Backbone listener so that when the Bokeh slider has a change
    # event, we can process the new data
    # @listenTo(@model.slider, 'change', () => @render())

  render: () ->
    super
    # Backbone Views create <div> elements by default, accessible as @el.
    # Many Bokeh views ignore this default <div>, and instead do things
    # like draw to the HTML canvas. In this case though, we change the
    # contents of the <div>, based on the current slider value.
    # empty(@el)
    # @el.appendChild(div({
    #   style: {
    #     color: '#686d8e'
    #     'background-color': '#2a3153'
    #   }
    # }, "#{@model.text}: #{@model.slider.value}"))

export class FlexLine extends Line

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
