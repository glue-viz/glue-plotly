from glue.viewers.scatter.state import DDCProperty, ScatterLayerState


class PlotlyScatterLayerState(ScatterLayerState):

    border_visible = DDCProperty(False, docstring="Whether to show borders on the markers")
    border_size = DDCProperty(1, docstring="The size of the marker borders")
    border_color = DDCProperty("#000000", docstring="The color of the marker borders")
    border_color_match_layer = DDCProperty(False, docstring="If true, border color options are ignored, "
                                                            "and the border matches the layer")
