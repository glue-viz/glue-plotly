from echo import CallbackProperty

from glue.core.state_objects import State
from glue.viewers.common.state import ViewerState


class PlotlyLegendState(State):

    visible = CallbackProperty(False, docstring="Whether to show the legend")
    title = CallbackProperty("", docstring="The title of the legend")
    frame_color = CallbackProperty("#ffffff", docstring="Frame color of the legend")
    show_edge = CallbackProperty(True,
                                 docstring="Whether to show the edge of the frame")
    text_color = CallbackProperty("#000000", docstring="Text color of the legend")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_default_colors()

    def _set_default_colors(self):
        from glue.config import settings

        self.frame_color = settings.BACKGROUND_COLOR
        self.text_color = settings.FOREGROUND_COLOR


class BasePlotlyViewerState(ViewerState):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.legend = PlotlyLegendState(*args, **kwargs)
