import os

from glue.core import Data
from glue_plotly.html_exporters.jupyter.tests.test_base import BaseTestJupyterExporter

from pytest import importorskip

importorskip('glue_jupyter')
importorskip('glue_vispy_viewers')

from glue_vispy_viewers.volume.jupyter import JupyterVispyVolumeViewer  # noqa: E402

from numpy import arange, ones  # noqa: E402


class TestVolume(BaseTestJupyterExporter):

    viewer_type = JupyterVispyVolumeViewer
    tool_id = 'save:jupyter_plotlyvolume'

    def make_data(self):
        return Data(label='d1',
                    x=arange(24).reshape((2, 3, 4)),
                    y=ones((2, 3, 4)),
                    z=arange(100, 124).reshape((2, 3, 4)))

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test_default.html')
        assert os.path.exists(output_path)
