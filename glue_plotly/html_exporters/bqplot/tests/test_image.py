import os

from glue.core import Data
from glue_jupyter.bqplot.image import BqplotImageView

from numpy import arange, ones

from .test_base import TestBqplotExporter


class TestImage(TestBqplotExporter):

    viewer_type = BqplotImageView
    tool_id = 'save:bqplot_plotlyimage2d'

    def test_data(self):
        return Data(label='d1', x=arange(24).reshape((2, 3, 4)), y=ones((2, 3, 4)))

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test_default.html')
        assert os.path.exists(output_path)
