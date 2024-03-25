from echo import CallbackProperty
from glue.viewers.common.state import ViewerState
from ipywidgets import VBox

from glue_plotly.viewers.common import PlotlyBaseView


class ExampleState(ViewerState):
    x_axislabel = CallbackProperty("")
    y_axislabel = CallbackProperty("")
    x_min = CallbackProperty(0)
    x_max = CallbackProperty(1)
    y_min = CallbackProperty(0)
    y_max = CallbackProperty(1)
    show_axes = CallbackProperty(True)

    def reset_limits(self):
        self.x_min = 0
        self.x_max = 1
        self.y_min = 0
        self.y_max = 1


class ExampleOptions(VBox):

    def __init__(self, viewer_state):

        self.state = viewer_state
        super().__init__([])


class ExampleViewer(PlotlyBaseView):

    _state_cls = ExampleState
    _options_cls = ExampleOptions

    tools = ['plotly:zoom', 'plotly:hzoom', 'plotly:vzoom',
             'plotly:pan', 'plotly:xrange', 'plotly:yrange',
             'plotly:rectangle', 'plotly:lasso', 'plotly:home',
             'plotly:hover']

    def __init__(self, session, state=None):
        super().__init__(session, state)
