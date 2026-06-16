import pytest

from glue.core import Data

pytest.importorskip("glue_qt")

from glue_qt.viewers.image.data_viewer import ImageViewer
from numpy import arange, ones

from glue_plotly.tests.helpers import html_screenshot_test
from .helpers import qt_export_figure


@html_screenshot_test
def test_image(tmp_path, page):
    data = Data(label="d1", x=arange(24).reshape((2, 3, 4)), y=ones((2, 3, 4)))
    output_path = str(tmp_path / "qt_image.html")
    qt_export_figure({
        "viewer_type": ImageViewer,
        "data": data,
        "tool_id": "save:plotlyimage2d",
        "output_path": output_path,
    })
    return output_path
