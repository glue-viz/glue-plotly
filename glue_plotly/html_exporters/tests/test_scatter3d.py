from __future__ import absolute_import, division, print_function

import os

import pytest
from mock import patch

from glue.core import Data
from glue.app.qt import GlueApplication

pytest.importorskip('glue_vispy_viewers')

from glue_vispy_viewers.scatter.scatter_viewer import VispyScatterViewer  # noqa


class TestScatter3D:

    def setup_method(self, method):
        self.data = Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label='d1')
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(VispyScatterViewer)
        self.viewer.add_data(self.data)
        for subtool in self.viewer.toolbar.tools['save'].subtools:
            if subtool.tool_id == 'save:plotly3d':
                self.tool = subtool
                break
        else:
            raise Exception("Could not find save:plotly2d tool in viewer")

    def teardown_method(self, method):
        self.viewer.close(warn=False)
        self.viewer = None
        self.app.close()
        self.app = None

    def test_default(self, tmpdir):
        output_file = tmpdir.join('test.html').strpath
        with patch('qtpy.compat.getsavefilename') as fd:
            fd.return_value = output_file, 'html'
            self.tool.activate()
        assert os.path.exists(output_file)
