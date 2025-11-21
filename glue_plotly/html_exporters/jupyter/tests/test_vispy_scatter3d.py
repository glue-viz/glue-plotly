import os

import pytest

from glue.core import Data

pytest.importorskip("glue_jupyter")
pytest.importorskip("glue_vispy_viewers")

from glue_vispy_viewers.scatter.jupyter import JupyterVispyScatterViewer  # noqa: E402

from glue_plotly.html_exporters.jupyter.tests.test_base import BaseTestJupyterExporter  # noqa: E402


class TestScatter3D(BaseTestJupyterExporter):

    viewer_type = JupyterVispyScatterViewer
    tool_id = "save:jupyter_plotly3dscatter"

    def make_data(self):
        return Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label="d1")

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, "test_default.html")
        assert os.path.exists(output_path)
