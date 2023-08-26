import os

from mock import patch

from glue.core import Data
from glue_qt.app import GlueApplication
from glue_qt.plugins.dendro_viewer.data_viewer import DendrogramViewer


class TestDendrogram:

    def setup_method(self, method):
        self.data = Data(label='dendrogram', parent=[-1, 0, 1, 1], height=[1.3, 2.2, 3.2, 4.4])
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(DendrogramViewer)
        self.viewer.add_data(self.data)
        for subtool in self.viewer.toolbar.tools['save'].subtools:
            if subtool.tool_id == 'save:plotlydendro':
                self.tool = subtool
                break
        else:
            raise Exception("Could not find save:plotlydendro tool in viewer")

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
