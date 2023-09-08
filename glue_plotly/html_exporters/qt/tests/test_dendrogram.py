from glue.core import Data
from glue_qt.plugins.dendro_viewer.data_viewer import DendrogramViewer

from .base import TestQtExporter


class TestDendrogram(TestQtExporter):

    viewer_type = DendrogramViewer
    tool_id = 'save:plotlydendro'

    def make_data(self):
        return Data(label='dendrogram', parent=[-1, 0, 1, 1], height=[1.3, 2.2, 3.2, 4.4])
