import pytest

pytest.importorskip("glue_qt")

from glue_plotly.tests.helpers import html_screenshot_test
from glue_plotly.html_exporters.qt.tests.helpers import qt_export_figure
from glue_qt.viewers.table import TableViewer


@html_screenshot_test
def test_table(tmp_path, page, data_xyz):
    output_path = str(tmp_path / "qt_table.html")
    qt_export_figure({
        "viewer_type": TableViewer,
        "data": data_xyz,
        "tool_id": "save:plotlytable",
        "output_path": output_path,
        "subtool": False,
    })
    return output_path
