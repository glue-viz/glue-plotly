import os

from glue.core import Data

from pytest import importorskip

importorskip('glue_qt.plugins.dendro_viewer.data_viewer')

from glue_qt.plugins.dendro_viewer.data_viewer import DendrogramViewer  # noqa

from .test_base import TestQtExporter  # noqa


class TestDendrogram(TestQtExporter):

    viewer_type = DendrogramViewer
    tool_id = 'save:plotlydendro'

    def make_data(self):
        return Data(label='dendrogram', parent=[-1, 0, 1, 1], height=[1.3, 2.2, 3.2, 4.4])

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test_default.html')
        assert os.path.exists(output_path)
