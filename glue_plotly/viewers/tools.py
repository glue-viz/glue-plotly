from glue.config import viewer_tool
from glue.viewers.common.tool import CheckableTool


class PlotlyDragMode(CheckableTool):

    def __init__(self, viewer, mode):
        super().__init__(viewer)
        self.mode = mode

    def activate(self):
        self.viewer.figure.update_layout(dragmode=self.mode)

    def deactivate(self):
        self.viewer.figure.update_layout(dragmode=False)


@viewer_tool
class PlotlyZoomMode(PlotlyDragMode):

    icon = 'glue_zoom_to_rect'
    tool_id = 'plotly:zoom'
    action_text = 'Zoom'
    tool_tip = 'Zoom to rectangle'

    def __init__(self, viewer):
        super().__init__(viewer, 'zoom')
        self.viewer = viewer


@viewer_tool
class PlotlyRectangleSelectionMode(PlotlyDragMode):

    icon = 'glue_square'
    tool_id = 'plotly:rectangle'
    action_text = 'Rectangular ROI'
    tool_tip = 'Define a rectangular region of interest'

    def __init__(self, viewer):
        super().__init__(viewer, 'select')


@viewer_tool
class PlotlyLassoSelectionMode(PlotlyDragMode):

    icon = 'glue_lasso'
    tool_id = 'plotly:lasso'
    action_text = 'Polygonal ROI'
    tool_tip = 'Lasso a region of interest'

    def __init__(self, viewer):
        super().__init__(viewer, "lasso")
