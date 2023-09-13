import os

import pytest

from glue.core import Data

pytest.importorskip('glue_vispy_viewers')

from glue_vispy_viewers.scatter.scatter_viewer import VispyScatterViewer  # noqa

from .test_base import TestQtExporter  # noqa


class TestScatter3D(TestQtExporter):

    viewer_type = VispyScatterViewer
    tool_id = 'save:plotly3d'

    def make_data(self):
        return Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label='d1')

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test.html')
        assert os.path.exists(output_path)
