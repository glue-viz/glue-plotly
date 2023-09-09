import os

from glue.core import Data
from glue_qt.viewers.image.data_viewer import ImageViewer

from numpy import arange, ones

from .test_base import TestQtExporter


class TestImage(TestQtExporter):

    viewer_type = ImageViewer
    tool_id = 'save:plotlyimage2d'

    def make_data(self):
        return Data(label='d1', x=arange(24).reshape((2, 3, 4)), y=ones((2, 3, 4)))

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test.html') 
        assert os.path.exists(output_path)
