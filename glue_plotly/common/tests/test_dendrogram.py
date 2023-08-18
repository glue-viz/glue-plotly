from numpy import log10
from plotly.graph_objs import Scatter
import pytest

from glue.config import settings
from glue.core import Data
from glue_qt.app import GlueApplication
from glue_qt.plugins.dendro_viewer import DendrogramViewer

from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.common import base_rectilinear_axis
from glue_plotly.common.dendrogram import trace_for_layer, x_axis


class TestDendrogram:

    def setup_method(self, method):
        self.data = Data(label='dendrogram', parent=[-1, 0, 1, 1], height=[1.3, 2.2, 3.2, 4.4])
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(DendrogramViewer)
        self.viewer.add_data(self.data)

        self.layer = self.viewer.layers[0]
        self.layer.state.linewidth = 4
        self.layer.state.alpha = 0.86
        self.layer.state.color = '#729fcf'

    def teardown_method(self, method):
        self.viewer.close(warn=False)
        self.viewer = None
        self.app.close()
        self.app = None

    def test_basic(self):
        export_layers = layers_to_export(self.viewer)
        assert len(export_layers) == 1
        assert data_count(export_layers) == 1

    @pytest.mark.parametrize('log_y', [True, False])
    def test_axes(self, log_y):
        self.viewer.state.y_log = log_y

        xaxis = x_axis(self.viewer.state)
        yaxis = base_rectilinear_axis(self.viewer.state, 'y')

        assert xaxis['showticklabels'] is False
        assert xaxis['showline'] is False
        assert xaxis['showgrid'] is False
        assert xaxis['range'] == [self.viewer.state.x_min, self.viewer.state.x_max]

        default_settings = dict(showgrid=False, showline=True, mirror=True, rangemode='normal',
                                zeroline=False, showspikes=False, showticklabels=True,
                                linecolor=settings.FOREGROUND_COLOR, tickcolor=settings.FOREGROUND_COLOR)
        assert default_settings.items() <= yaxis.items()

        assert yaxis['type'] == 'log' if log_y else 'linear'
        expected_y_range = [self.viewer.state.y_min, self.viewer.state.y_max]
        if log_y:
            expected_y_range = list(log10(expected_y_range))
        assert yaxis['range'] == expected_y_range
        if log_y:
            assert yaxis['dtick'] == 1
            assert yaxis['minor_ticks'] == 'outside'

    def test_trace(self):
        xy_data = self.layer.mpl_artists[0].get_xydata()
        trace = trace_for_layer(self.layer.state, xy_data)
        assert isinstance(trace, Scatter)
        assert trace['mode'] == 'lines'
        assert trace['name'] == 'dendrogram'
        assert trace['hoverinfo'] == 'skip'
        assert trace['opacity'] == 0.86
        line = trace['line']
        assert line['width'] == 6
        assert line['color'] == '#729fcf'
