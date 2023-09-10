import os

from glue.core import Data

from pytest import importorskip

importorskip('glue_qt')

from glue_qt.viewers.scatter import ScatterViewer  # noqa

from .test_base import TestQtExporter  # noqa


class TestScatter2D(TestQtExporter):

    viewer_type = ScatterViewer
    tool_id = 'save:plotly2d'

    def make_data(self):
        return Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label='d1')

    def test_default(self, tmpdir):
        self.viewer.state.plot_mode = 'rectilinear'
        output_path = self.export_figure(tmpdir, 'test_rectilinear.html')
        assert os.path.exists(output_path)

    def test_polar_radians(self, tmpdir):
        self.viewer.state.plot_mode = 'polar'
        self.viewer.state.angle_unit = 'radians'
        output_path = self.export_figure(tmpdir, 'test_polar_radians.html')
        assert os.path.exists(output_path)

    def test_polar_degrees(self, tmpdir):
        self.viewer.state.plot_mode = 'polar'
        self.viewer.state.angle_unit = 'degrees'
        output_path = self.export_figure(tmpdir, 'test_polar_degrees.html')
        assert os.path.exists(output_path)
