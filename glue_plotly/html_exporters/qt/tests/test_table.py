import os

from glue.core import Data

from pytest import importorskip

importorskip('glue_qt')

from glue_qt.app import GlueApplication  # noqa
from glue_qt.viewers.table import TableViewer  # noqa

from .test_base import TestQtExporter  # noqa


class TestTable(TestQtExporter):

    viewer_type = TableViewer
    tool_id = 'save:plotlytable'

    def setup_method(self, method):
        self.data = Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label='d1')
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(self.viewer_type)
        self.viewer.add_data(self.data)
        self.tool = self.viewer.toolbar.tools[self.tool_id]

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test.html')
        assert os.path.exists(output_path)
