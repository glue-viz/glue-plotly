from glue.core import Data
from glue_jupyter import JupyterApplication
from plotly.graph_objects import Bar

from glue_plotly.common import DEFAULT_FONT
from glue_plotly.viewers.common.tests import BasePlotlyViewTests
from glue_plotly.viewers.histogram import PlotlyHistogramView


class TestHistogramViewer(BasePlotlyViewTests):

    def setup_method(self, method):
        self.data = Data(label="histogram", x=[1, 1, 1, 2, 2, 3, 3, 3, 4, 6, 6])
        self.app = JupyterApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(PlotlyHistogramView)
        self.viewer.add_data(self.data)

        viewer_state = self.viewer.state
        viewer_state.x_min = 0.5
        viewer_state.hist_x_min = 0.5
        viewer_state.x_max = 6.5
        viewer_state.hist_x_max = 6.5
        viewer_state.hist_n_bin = 6
        viewer_state.y_min = 0
        viewer_state.y_max = 5
        viewer_state.x_axislabel = 'X Axis'
        viewer_state.y_axislabel = 'Y Axis'
        viewer_state.normalize = False

        self.layer = self.viewer.layers[0]
        self.layer.state.color = "#abcdef"
        self.layer.state.alpha = 0.75

    def teardown_method(self, method):
        self.viewer = None
        self.app = None

    def test_basic(self):
        assert len(self.viewer.layers) == 1
        traces = list(self.layer.traces())
        assert len(traces) == 1
        bars = traces[0]
        assert isinstance(bars, Bar)
        assert bars.marker.color == "#abcdef"
        assert bars.marker.opacity == 0.75
        assert bars.x == tuple(range(1, 7))
        expected_y = [3, 2, 3, 1, 0, 2]
        assert all(a == b for a, b in zip(bars.y, expected_y))

    def test_axes(self):
        x_axis = self.viewer.figure.layout.xaxis
        y_axis = self.viewer.figure.layout.yaxis

        assert x_axis.title.text == 'X Axis'
        assert y_axis.title.text == 'Y Axis'
        assert x_axis.type == 'linear'
        assert y_axis.type == 'linear'

        assert x_axis.range == (0.5, 6.5)
        assert y_axis.range == (0, 5)

        assert all(f.family == DEFAULT_FONT for f in
                   (x_axis.title.font, x_axis.tickfont, y_axis.title.font, y_axis.tickfont))

        common_items = dict(showgrid=False, showline=True, mirror=True, rangemode='normal',
                            zeroline=False, showspikes=False, showticklabels=True)
        for axis in x_axis, y_axis:
            assert all(axis[key] == value for key, value in common_items.items())

    def test_gaps(self):
        assert self.viewer.figure.layout.bargap == 0
        self.viewer.state.gaps = True
        assert self.viewer.figure.layout.bargap == 0.15
        self.viewer.state.gap_fraction = 0.36
        assert self.viewer.figure.layout.bargap == 0.36
        self.viewer.state.gaps = False
        assert self.viewer.figure.layout.bargap == 0
