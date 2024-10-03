import os

from glue.core import Data
from glue_plotly.html_exporters.jupyter.tests.test_base import BaseTestJupyterExporter

from pytest import importorskip

importorskip('glue_jupyter')

from glue_jupyter.ipyvolume import IpyvolumeScatterView  # noqa: E402


class TestScatter3D(BaseTestJupyterExporter):

    viewer_type = IpyvolumeScatterView
    tool_id = 'save:jupyter_plotly3dscatter'

    def make_data(self):
        return Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label='d1')

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test_default.html')
        assert os.path.exists(output_path)
