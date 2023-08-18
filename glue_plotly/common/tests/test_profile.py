from itertools import product

from numpy import arange, log10
import pytest

from glue.config import settings
from glue.core import Data
from glue_qt.app import GlueApplication
from glue_qt.viewers.profile import ProfileViewer

from glue_plotly.common import DEFAULT_FONT, data_count, layers_to_export, sanitize
from glue_plotly.common.profile import axis_from_mpl, traces_for_layer

from glue_plotly.common.tests.utils import SimpleCoordinates


class TestProfile:

    def setup_method(self, method):
        self.data = Data(label='profile', w=arange(0, 240, 10).reshape((3, 4, 2)).astype(float))
        self.data.coords = SimpleCoordinates()
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(ProfileViewer)
        self.viewer.add_data(self.data)
        self.mask, self.sanitized = sanitize(self.data['w'])

        viewer_state = self.viewer.state
        viewer_state.x_axislabel_size = 15
        viewer_state.y_axislabel_size = 10
        viewer_state.x_ticklabel_size = 6
        viewer_state.y_ticklabel_size = 12
        viewer_state.x_min = 1
        viewer_state.x_max = 250
        viewer_state.y_min = 0
        viewer_state.y_max = 5
        viewer_state.x_axislabel = 'X Axis'
        viewer_state.y_axislabel = 'Y Axis'

        self.layer = self.viewer.layers[0]
        self.layer.state.linewidth = 3
        self.layer.state.as_steps = False
        self.layer.state.color = '#ff0000'
        self.layer.state.alpha = 0.75

    def teardown_method(self, method):
        self.viewer.close(warn=False)
        self.viewer = None
        self.app.close()
        self.app = None

    def test_basic(self):
        export_layers = layers_to_export(self.viewer)
        assert len(export_layers) == 1
        assert data_count(export_layers) == 1
        assert sum(sum(sum(self.mask))) == 24

    @pytest.mark.parametrize('log_x, log_y', product([True, False], repeat=2))
    def test_axes(self, log_x, log_y):
        self.viewer.state.x_log = log_x
        self.viewer.state.y_log = log_y
        self.viewer.state.x_axislabel = 'X Axis'
        self.viewer.state.y_axislabel = 'Y Axis'

        x_axis = axis_from_mpl(self.viewer, 'x')
        y_axis = axis_from_mpl(self.viewer, 'y')

        common_items = dict(showgrid=False, showline=True, mirror=True, rangemode='normal',
                            zeroline=False, showspikes=False, showticklabels=True,
                            linecolor=settings.FOREGROUND_COLOR, tickcolor=settings.FOREGROUND_COLOR)
        assert common_items.items() <= x_axis.items()
        assert common_items.items() <= y_axis.items()

        assert x_axis['title'] == 'X Axis'
        assert y_axis['title'] == 'Y Axis'
        assert x_axis['type'] == 'log' if log_x else 'linear'
        assert y_axis['type'] == 'log' if log_y else 'linear'

        expected_x_range = [self.viewer.state.x_min, self.viewer.state.x_max]
        expected_y_range = [self.viewer.state.y_min, self.viewer.state.y_max]
        if log_x:
            expected_x_range = list(log10(expected_x_range))
        if log_y:
            expected_y_range = list(log10(expected_y_range))
        assert x_axis['range'] == expected_x_range
        assert y_axis['range'] == expected_y_range

        base_font_dict = dict(family=DEFAULT_FONT, color=settings.FOREGROUND_COLOR)
        assert x_axis['titlefont'] == dict(**base_font_dict, size=30)
        assert y_axis['titlefont'] == dict(**base_font_dict, size=20)
        assert x_axis['tickfont'] == dict(**base_font_dict, size=9)
        assert y_axis['tickfont'] == dict(**base_font_dict, size=18)

        if log_x:
            assert x_axis['dtick'] == 1
            assert x_axis['minor_ticks'] == 'outside'
        if log_y:
            assert y_axis['dtick'] == 1
            assert y_axis['minor_ticks'] == 'outside'

    @pytest.mark.parametrize('as_steps', [True, False])
    def test_trace(self, as_steps):
        self.layer.state.as_steps = as_steps
        traces = traces_for_layer(self.viewer.state, self.layer.state)
        assert len(traces) == 1
        trace = traces[0]
        line = trace['line']
        assert line['width'] == 6
        assert line['shape'] == 'hvh' if as_steps else 'linear'
        assert line['color'] == '#ff0000'
        assert trace['opacity'] == 0.75
        assert trace['name'] == 'profile'
        assert trace['hoverinfo'] == 'skip'
