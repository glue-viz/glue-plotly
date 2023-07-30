from contextlib import nullcontext
from glue.config import viewer_tool
from glue.core.subset import PolygonalROI, RectangularROI, XRangeROI, YRangeROI
from glue.viewers.common.tool import CheckableTool, Tool


class PlotlyDragMode(CheckableTool):

    def __init__(self, viewer, mode):
        super().__init__(viewer)
        self.mode = mode

    def activate(self):

        # Disable any active tool in other viewers
        if self.viewer.session.application.get_setting('single_global_active_tool'):
            for viewer in self.viewer.session.application.viewers:
                if viewer is not self.viewer:
                    viewer.toolbar.active_tool = None

        self.viewer.figure.update_layout(dragmode=self.mode)

    def deactivate(self):
        self.viewer.figure.update_layout(dragmode=False)


class PlotlySelectionMode(PlotlyDragMode):

    def activate(self):
        super().activate()
        self.viewer.set_selection_active(True)
        self.viewer.set_selection_callback(self.on_selection)

    def deactivate(self):
        print("Deactivating")
        self.viewer.set_selection_callback(None)
        self.viewer.set_selection_active(False)
        self.viewer.figure.on_edits_completed(self._clear_selection)

    def _clear_selection(self):
        self.viewer.figure.plotly_relayout({'selections':[], 'dragmode': False})

    def on_selection(self, trace, points, selector):
        print("In on_selection")
        self._on_selection(trace, points, selector)
        self.viewer.toolbar.active_tool = None
        self.deactivate()


@viewer_tool
class PlotlyZoomMode(PlotlyDragMode):

    icon = 'glue_zoom_to_rect'
    tool_id = 'plotly:zoom'
    action_text = 'Zoom'
    tool_tip = 'Zoom to rectangle'

    def __init__(self, viewer):
        super().__init__(viewer, 'zoom')


@viewer_tool
class PlotlyPanMode(PlotlyDragMode):

    icon = 'glue_move'
    tool_id = 'plotly:pan'
    action_text = 'Pan'
    tool_tip = 'Interactively pan'

    def __init__(self, viewer):
        super().__init__(viewer, 'pan')


@viewer_tool
class PlotlyHRangeSelectionMode(PlotlySelectionMode):

    icon = 'glue_xrange_select'
    tool_id = 'plotly:xrange'
    action_text = 'X range'
    tool_tip = 'Select a range of x values'

    def __init__(self, viewer):
        super().__init__(viewer, 'select')

    def activate(self):
        super().activate()
        self.viewer.figure.update_layout(selectdirection="h")

    def _on_selection(self, _trace, _points, selector):
        xmin, xmax = selector.xrange
        roi = XRangeROI(xmin, xmax)
        with self.viewer._output_widget or nullcontext():
            self.viewer.apply_roi(roi)


@viewer_tool
class PlotlyVRangeSelectionMode(PlotlySelectionMode):

    icon = 'glue_yrange_select'
    tool_id = 'plotly:yrange'
    action_text = 'Y range'
    tool_tip = 'Select a range of y values'

    def __init__(self, viewer):
        super().__init__(viewer, 'select')

    def activate(self):
        super().activate()
        self.viewer.figure.update_layout(selectdirection="v")

    def _on_selection(self, _trace, _points, selector):
        ymin, ymax = selector.yrange
        roi = YRangeROI(ymin, ymax)
        with self.viewer._output_widget or nullcontext():
            self.viewer.apply_roi(roi)


@viewer_tool
class PlotlyRectangleSelectionMode(PlotlySelectionMode):

    icon = 'glue_square'
    tool_id = 'plotly:rectangle'
    action_text = 'Rectangular ROI'
    tool_tip = 'Define a rectangular region of interest'

    def __init__(self, viewer):
        super().__init__(viewer, 'select')

    def activate(self):
        super().activate()
        self.viewer.figure.update_layout(selectdirection="any")

    def _on_selection(self, _trace, _points, selector):
        xmin, xmax = selector.xrange
        ymin, ymax = selector.yrange
        roi = RectangularROI(xmin, xmax, ymin, ymax)
        with self.viewer._output_widget or nullcontext():
            self.viewer.apply_roi(roi)

@viewer_tool
class PlotlyLassoSelectionMode(PlotlySelectionMode):

    icon = 'glue_lasso'
    tool_id = 'plotly:lasso'
    action_text = 'Polygonal ROI'
    tool_tip = 'Lasso a region of interest'

    def __init__(self, viewer):
        super().__init__(viewer, "lasso")


    def _on_selection(self, _trace, _points, selector):
        roi = PolygonalROI(selector.xs, selector.ys)
        with self.viewer._output_widget or nullcontext():
            self.viewer.apply_roi(roi)


@viewer_tool
class PlotlyHomeTool(Tool):

    icon = 'glue_home'
    tool_id = 'plotly:home'
    action_text = 'Home'
    tool_tip = 'Reset original zoom'

    def activate(self):
        with self.viewer.figure.batch_update():
            self.viewer.state.reset_limits()