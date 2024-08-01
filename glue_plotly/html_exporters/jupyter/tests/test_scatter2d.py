import os

from glue.core import Data

from pytest import importorskip

importorskip('glue_jupyter')

from glue_jupyter.bqplot.scatter import BqplotScatterView  # noqa

from .test_base import TestBqplotExporter  # noqa


class TestScatter2D(TestBqplotExporter):

    viewer_type = BqplotScatterView
    tool_id = 'save:bqplot_plotly2d'

    def make_data(self):
        return Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label='d1')

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test_default.html')
        assert os.path.exists(output_path)
