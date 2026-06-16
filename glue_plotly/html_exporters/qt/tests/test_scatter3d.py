import pytest

pytest.importorskip("glue_qt")
pytest.importorskip("glue_vispy_viewers")

from glue_plotly.html_exporters.qt.tests.helpers import qt_export_figure
from glue_plotly.tests.helpers import html_screenshot_test
from glue_vispy_viewers.scatter.qt.scatter_viewer import (
    VispyScatterViewer,
)

@html_screenshot_test
def test_scatter3d(tmp_path, page, data_xyz):
    output_path = str(tmp_path / "qt_scatter3d.html")
    qt_export_figure({
        "viewer_type": VispyScatterViewer,
        "data": data_xyz,
        "tool_id": "save:plotly3d",
        "output_path": output_path
    })
    return output_path
