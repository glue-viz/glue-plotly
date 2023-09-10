import os

from glue.core import Data

from pytest import importorskip

importorskip('glue_qt')

from glue_qt.viewers.histogram import HistogramViewer  # noqa

from .test_base import TestQtExporter  # noqa


class TestHistogram(TestQtExporter):

    viewer_type = HistogramViewer
    tool_id = 'save:plotlyhist'

    def make_data(self):
        return Data(x=[40, 41, 37, 63, 78, 35, 19, 100, 35, 86, 84, 99,
                       87, 56, 2, 71, 22, 36, 10, 1, 26, 70, 45, 20, 8],
                    label='d1')

    def test_default(self, tmpdir):
        self.viewer.state.x_att = self.data.id['x']
        self.viewer.state.hist_n_bin = 6
        output_path = self.export_figure(tmpdir, 'test_default.html')
        assert os.path.exists(output_path)
