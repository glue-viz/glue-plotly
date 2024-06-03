import os

from glue.core import Data

from pytest import importorskip

importorskip('glue_qt')
importorskip('glue_vispy_viewers')

from glue_vispy_viewers.volume.qt.volume_viewer import VispyVolumeViewer  # noqa: E402

from numpy import arange, ones  # noqa: E402

from .test_base import TestQtExporter  # noqa: E402


class TestVolume(TestQtExporter):

    viewer_type = VispyVolumeViewer
    tool_id = 'save:plotlyvolume'

    def make_data(self):
        return Data(label='d1',
                    x=arange(24).reshape((2, 3, 4)),
                    y=ones((2, 3, 4)),
                    z=arange(100, 124).reshape((2, 3, 4)))

    def test_default(self, tmpdir):
        output_path = self.export_figure(tmpdir, 'test.html')
        assert os.path.exists(output_path)
