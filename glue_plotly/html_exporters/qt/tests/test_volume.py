import pytest

from glue.core import Data

pytest.importorskip("glue_qt")
pytest.importorskip("glue_vispy_viewers")

from glue_plotly.html_exporters.qt.tests.helpers import qt_export_figure
from glue_plotly.tests.helpers import html_screenshot_test
from glue_vispy_viewers.volume.qt.volume_viewer import VispyVolumeViewer
from numpy import arange, ones


@html_screenshot_test
def test_volume(tmp_path, page):
    data = Data(label="d1",
                x=arange(24).reshape((2, 3, 4)),
                y=ones((2, 3, 4)),
                z=arange(100, 124).reshape((2, 3, 4)))
    output_path = str(tmp_path / "qt_volume.html")
    qt_export_figure({
        "viewer_type": VispyVolumeViewer,
        "data": data,
        "tool_id": "save:plotlyvolume",
        "output_path": output_path,
    })
    return output_path
