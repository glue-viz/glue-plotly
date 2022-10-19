import os

from mock import patch
import numpy as np

from glue.core import Data
from glue.app.qt import GlueApplication
from glue.viewers.image.qt import ImageViewer


class TestImage:

    def setup_method(self, method):
        self.data = Data(label='d1', x=np.arange(24).reshape((2, 3, 4)), y=np.ones((2, 3, 4)))
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(ImageViewer)
        self.viewer.add_data(self.data)
        for subtool in self.viewer.toolbar.tools['save'].subtools:
            if subtool.tool_id == 'save:plotlyimage2d':
                self.tool = subtool
                break
        else:
            raise Exception("Could not find save:plotlyimage2d tool in viewer")

    def teardown_method(self, method):
        self.viewer.close(warn=False)
        self.viewer = None
        self.app.close()
        self.app = None

    def export_figure(self, tmpdir, output_filename):
        output_path = tmpdir.join(output_filename).strpath
        with patch('qtpy.compat.getsavefilename') as fd:
            fd.return_value = output_path, 'html'
            self.tool.activate()
        return output_path

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test_default.html')
        assert os.path.exists(output_path)
