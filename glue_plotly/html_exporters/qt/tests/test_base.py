from mock import patch

from glue_qt.app import GlueApplication
from glue_plotly.save_hover import SaveHoverDialog
from glue_plotly.sort_components import SortComponentsDialog
from qtpy.QtWidgets import QMessageBox


class TestQtExporter:

    viewer_type = None
    tool_id = None

    def setup_method(self, method):
        self.data = self.make_data()
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(self.viewer_type)
        self.viewer.add_data(self.data)
        for subtool in self.viewer.toolbar.tools['save'].subtools:
            if subtool.tool_id == self.tool_id:
                self.tool = subtool
                break
        else:
            raise Exception(f"Could not find {self.tool_id} tool in viewer")

    def teardown_method(self, method):
        self.viewer.close(warn=False)
        self.viewer = None
        self.app.close()
        self.app = None

    def auto_accept_selectdialog(self):
        def exec_replacement(dialog):
            dialog.select_all()
            dialog.accept()
        return exec_replacement

    def auto_accept_messagebox(self):
        def exec_replacement(box):
            box.accept()
        return exec_replacement

    def export_figure(self, tmpdir, output_filename):
        output_path = tmpdir.join(output_filename).strpath
        with patch('qtpy.compat.getsavefilename') as fd:
            fd.return_value = output_path, 'html'
            with patch.object(SaveHoverDialog, 'exec_', self.auto_accept_selectdialog()), \
                 patch.object(SortComponentsDialog, 'exec_', self.auto_accept_selectdialog()), \
                 patch.object(QMessageBox, 'exec_', self.auto_accept_messagebox()):
                self.tool.activate()
        return output_path
