import os

from glue.core import Data
from glue.tests.helpers import make_skipper

from pytest import importorskip

importorskip('glue_qt.plugins.dendro_viewer.data_viewer')

from glue_qt.plugins.dendro_viewer.data_viewer import DendrogramViewer  # noqa: E402

from .test_base import TestQtExporter  # noqa: E402


NUMPY_LT_2, requires_numpy_lt2 = make_skipper('numpy', version='2.0', skip_if='ge')


# Workaround until for the issue solved in https://github.com/glue-viz/glue-qt/pull/19
@requires_numpy_lt2
class TestDendrogram(TestQtExporter):

    viewer_type = DendrogramViewer
    tool_id = 'save:plotlydendro'

    def make_data(self):
        return Data(label='dendrogram', parent=[-1, 0, 1, 1], height=[1.3, 2.2, 3.2, 4.4])

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test_default.html')
        assert os.path.exists(output_path)
