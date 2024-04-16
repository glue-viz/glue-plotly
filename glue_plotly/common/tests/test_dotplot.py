from numpy import unique
from plotly.graph_objs import Scatter

from glue.core import Data
from glue_qt.app import GlueApplication
from glue_qt.viewers.histogram import HistogramViewer

from glue_plotly.common import sanitize
from glue_plotly.common.dotplot import traces_for_layer

from glue_plotly.viewers.histogram.viewer import PlotlyHistogramView
from glue_plotly.viewers.histogram.dotplot_layer_artist import PlotlyDotplotLayerArtist


class SimpleDotplotViewer(PlotlyHistogramView):
    _data_artist_cls = PlotlyDotplotLayerArtist
    _subset_artist_cls = PlotlyDotplotLayerArtist


class TestDotplot:

    def setup_method(self, method):
        x = [86,  86,  76,  78,  93, 100,  90,  87,  73,  61,  71,  68,  78,
             9,  87,  32,  34,   2,  57,  79,  48,   5,   8,  19,   7,  78,
             16,  15,  58,  34,  20,  63,  96,  97,  86,  92,  35,  59,  75,
             0,  53,  45,  59,  74,  59,   4,  69,  76,  97,  77,  24,  99,
             50,   6,   1,  55,  13,  40,  27,  17,  92,  72,  40,  29,  64,
             38,  77,  11,  91,  23,  59,  92,   5,  88,  15,  90,  40, 100,
             47,  28,   3,  44,  89,  75,  13,  94,  95,  43,  17,  88,   6,
             94, 100,  28,  45,  36,  63,  14,  90,  66]
        self.data = Data(label="dotplot", x=x)
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(HistogramViewer)
        self.viewer.add_data(self.data)
        self.mask, self.sanitized = sanitize(self.data['x'])

        viewer_state = self.viewer.state
        viewer_state.hist_n_bin = 18
        viewer_state.x_axislabel_size = 14
        viewer_state.y_axislabel_size = 8
        viewer_state.x_ticklabel_size = 18
        viewer_state.y_ticklabel_size = 20
        viewer_state.x_min = 0
        viewer_state.x_max = 100
        viewer_state.y_min = 0
        viewer_state.y_max = 15
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

    def test_basic_dots(self):
        traces = traces_for_layer(self.viewer, self.layer.state)
        assert len(traces) == 1
        dots = traces[0]
        assert isinstance(dots, Scatter)

        assert len(unique(dots.x)) == 18
        expected_y = (1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 1,
                      2, 3, 4, 5, 6, 1, 2, 3, 4, 1, 2, 3, 1, 2,
                      3, 4, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2,
                      3, 4, 5, 1, 2, 1, 2, 3, 4, 5, 6, 7, 1, 2,
                      3, 4, 1, 2, 3, 4, 1, 2, 3, 4, 5, 6, 7, 8,
                      1, 2, 3, 4, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3,
                      4, 5, 6, 7, 8, 9, 10, 11, 1, 2, 3, 4, 5,
                      6, 7, 8)

        assert dots.y == expected_y
        assert dots.marker.size == 16  # Default figure is 640x480
