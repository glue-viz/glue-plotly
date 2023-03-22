import os

from mock import patch

from glue.core import Data
from glue.app.qt import GlueApplication
from glue.viewers.profile.qt import ProfileViewer


class TestProfile:

    def setup_method(self, method):
        self.data = Data(x=[40, 41, 37, 63, 78, 35, 19, 100, 35, 86, 84, 99,
                            87, 56, 2, 71, 22, 36, 10, 1, 26, 70, 45, 20, 8],
                         label='d1')
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(ProfileViewer)
        self.viewer.add_data(self.data)
        for subtool in self.viewer.toolbar.tools['save'].subtools:
            if subtool.tool_id == 'save:plotlyprofile':
                self.tool = subtool
                break
        else:
            raise Exception("Could not find save:plotlyprofile tool in viewer")

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
        self.viewer.state.x_att = self.data.id['Pixel Axis 0 [x]']
        output_path = self.export_figure(tmpdir, 'test_default.html')
        assert os.path.exists(output_path)
