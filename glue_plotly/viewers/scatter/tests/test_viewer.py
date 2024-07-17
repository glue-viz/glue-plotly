from numpy import array_equal

from glue.core import Data
from glue_jupyter import JupyterApplication
from plotly.graph_objects import Scatter

from glue_plotly.common import DEFAULT_FONT
from glue_plotly.viewers.common.tests import BasePlotlyViewTests
from glue_plotly.viewers.scatter import PlotlyScatterView


class TestScatterView(BasePlotlyViewTests):

    def setup_method(self, method):
        super().setup_method(method)
        self.data = Data(label="histogram", x=[1, 3, 5, 7, 9], y=[2, 4, 6, 8, 10])
        self.app = JupyterApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(PlotlyScatterView)
        self.viewer.add_data(self.data)

        viewer_state = self.viewer.state
        viewer_state.x_min = 0
        viewer_state.x_max = 10
        viewer_state.y_min = 0
        viewer_state.y_max = 12
        viewer_state.x_axislabel = 'X Axis'
        viewer_state.y_axislabel = 'Y Axis'
        viewer_state.normalize = False

        self.layer = self.viewer.layers[0]
        self.layer.state.color = "#abcdef"
        self.layer.state.alpha = 0.75

    def teardown_method(self, method):
        self.viewer = None
        self.app = None
        super().teardown_method(method)

    def test_basic(self):
        assert len(self.viewer.layers) == 1
        traces = list(self.layer.traces())
        assert len(traces) == 1
        scatter = traces[0]
        assert isinstance(scatter, Scatter)
        assert scatter.marker.color == "#abcdef"
        assert scatter.marker.opacity == 0.75
        assert array_equal(scatter.x, self.data['x'])
        assert array_equal(scatter.y, self.data['y'])

    def test_axes(self):
        x_axis = self.viewer.figure.layout.xaxis
        y_axis = self.viewer.figure.layout.yaxis

        assert x_axis.title.text == 'X Axis'
        assert y_axis.title.text == 'Y Axis'
        assert x_axis.type == 'linear'
        assert y_axis.type == 'linear'

        assert x_axis.range == (0, 10)
        assert y_axis.range == (0, 12)

        assert all(f.family == DEFAULT_FONT for f in
                   (x_axis.title.font, x_axis.tickfont, y_axis.title.font, y_axis.tickfont))

        common_items = dict(showgrid=False, showline=True, mirror=True, rangemode='normal',
                            zeroline=False, showspikes=False, showticklabels=True)
        for axis in x_axis, y_axis:
            assert all(axis[key] == value for key, value in common_items.items())
