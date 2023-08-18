from __future__ import absolute_import, division, print_function

import os

from mock import patch

from glue.core import Data
from glue_qt.app import GlueApplication
from glue_qt.viewers.scatter import ScatterViewer
from glue_plotly.save_hover import SaveHoverDialog


def auto_accept():
    def exec_replacement(self):
        self.select_all()
        self.accept()
    return exec_replacement


class TestScatter2D:

    def setup_method(self, method):
        self.data = Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label='d1')
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(ScatterViewer)
        self.viewer.add_data(self.data)
        for subtool in self.viewer.toolbar.tools['save'].subtools:
            if subtool.tool_id == 'save:plotly2d':
                self.tool = subtool
                break
        else:
            raise Exception("Could not find save:plotly2d tool in viewer")

    def teardown_method(self, method):
        self.viewer.close(warn=False)
        self.viewer = None
        self.app.close()
        self.app = None

    def export_figure(self, tmpdir, output_filename):
        output_path = tmpdir.join(output_filename).strpath
        with patch('qtpy.compat.getsavefilename') as fd:
            fd.return_value = output_path, 'html'
            with patch.object(SaveHoverDialog, 'exec_', auto_accept()):
                self.tool.activate()
        return output_path

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
