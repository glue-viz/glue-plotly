from itertools import product

from numpy import log10
from plotly.graph_objs import Bar
import pytest

from glue.config import settings
from glue.core import Data
from glue_qt.app import GlueApplication
from glue_qt.viewers.histogram import HistogramViewer

from glue_plotly.common import DEFAULT_FONT, data_count, layers_to_export, sanitize
from glue_plotly.common.histogram import axis_from_mpl, traces_for_layer


class TestHistogram:

    def setup_method(self, method):
        self.data = Data(label="histogram", x=[3.4, -2.3, -1.1, 0.3])
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(HistogramViewer)
        self.viewer.add_data(self.data)
        self.mask, self.sanitized = sanitize(self.data['x'])

        viewer_state = self.viewer.state
        viewer_state.x_axislabel_size = 14
        viewer_state.y_axislabel_size = 8
        viewer_state.x_ticklabel_size = 18
        viewer_state.y_ticklabel_size = 20
        viewer_state.x_min = 1
        viewer_state.x_max = 250
        viewer_state.y_min = 0
        viewer_state.y_max = 5
        viewer_state.x_axislabel = 'X Axis'
        viewer_state.y_axislabel = 'Y Axis'

        self.layer = self.viewer.layers[0]
        self.layer.state.color = '#0e1dab'
        self.layer.state.alpha = 0.85

    def teardown_method(self, method):
        self.viewer.close(warn=False)
        self.viewer = None
        self.app.close()
        self.app = None

    def test_basic(self):
        export_layers = layers_to_export(self.viewer)
        assert len(export_layers) == 1
        assert data_count(export_layers) == 1
        assert sum(self.mask) == 4

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
        assert x_axis['titlefont'] == dict(**base_font_dict, size=28)
        assert y_axis['titlefont'] == dict(**base_font_dict, size=16)
        assert x_axis['tickfont'] == dict(**base_font_dict, size=27)
        assert y_axis['tickfont'] == dict(**base_font_dict, size=30)

        if log_x:
            assert x_axis['dtick'] == 1
            assert x_axis['minor_ticks'] == 'outside'
        if log_y:
            assert y_axis['dtick'] == 1
            assert y_axis['minor_ticks'] == 'outside'

    def test_basic_trace(self):
        traces = traces_for_layer(self.viewer.state, self.layer.state)
        assert len(traces) == 1
        trace = traces[0]
        assert isinstance(trace, Bar)

    def test_log_trace(self):
        self.viewer.state.x_log = True
        self.viewer.state.hist_n_bin = 3
        edges, _ = self.layer.state.histogram
        traces = traces_for_layer(self.viewer.state, self.layer.state)
        assert len(traces) == len(edges) - 1
        legend_group = traces[0]['legendgroup']
        for index, trace in enumerate(traces):
            assert trace['legendgroup'] == legend_group
            assert trace['showlegend'] == (index == 0)
            assert trace['width'] == edges[index + 1] - edges[index]
