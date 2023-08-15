import os

from mock import patch

from glue.core import Data
from glue_qt.app import GlueApplication
from glue_qt.viewers.table import TableViewer
from glue_plotly.sort_components import SortComponentsDialog
from qtpy.QtWidgets import QMessageBox


def auto_accept_sortdialog():
    def exec_replacement(self):
        self.select_all()
        self.accept()

    return exec_replacement


def auto_accept_messagebox():
    def exec_replacement(self):
        self.accept()

    return exec_replacement


class TestTable:

    def setup_method(self, method):
        self.data = Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label='d1')
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(TableViewer)
        self.viewer.add_data(self.data)
        self.tool = self.viewer.toolbar.tools['save:plotlytable']

    def teardown_method(self, method):
        self.viewer.close(warn=False)
        self.viewer = None
        self.app.close()
        self.app = None

    def test_default(self, tmpdir):
        output_file = tmpdir.join('test.html').strpath
        with patch('qtpy.compat.getsavefilename') as fd:
            fd.return_value = output_file, 'html'
            with patch.object(SortComponentsDialog, 'exec_', auto_accept_sortdialog()), \
                 patch.object(QMessageBox, 'exec_', auto_accept_messagebox()):
                self.tool.activate()
        assert os.path.exists(output_file)
