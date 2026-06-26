import pytest

pytest.importorskip("glue_qt")

from glue_qt.viewers.scatter import ScatterViewer

from glue.viewers.scatter.state import ScatterViewerState
from glue_plotly.tests.helpers import html_screenshot_test

from .helpers import qt_export_figure


@html_screenshot_test
def test_scatter2d(tmp_path, page, data_xyz):
    output_path = str(tmp_path / "qt_scatter2d_default.html")
    viewer_state = ScatterViewerState(plot_mode="rectilinear")
    qt_export_figure({
        "viewer_type": ScatterViewer,
        "data": data_xyz,
        "tool_id": "save:plotly2d",
        "output_path": output_path,
        "viewer_state": viewer_state,
    })
    return output_path


@html_screenshot_test
def test_scatter2d_polar_radians(tmp_path, page, data_xyz):
    output_path = str(tmp_path / "qt_scatter2d_polar_radians.html")
    viewer_state = ScatterViewerState(plot_mode="polar", angle_unit="radians")
    qt_export_figure({
        "viewer_type": ScatterViewer,
        "data": data_xyz,
        "tool_id": "save:plotly2d",
        "output_path": output_path,
        "viewer_state": viewer_state,
    })
    return output_path


@html_screenshot_test
def test_scatter2d_polar_degrees(tmp_path, page, data_xyz):
    output_path = str(tmp_path / "qt_scatter2d_polar_degrees.html")
    viewer_state = ScatterViewerState(plot_mode="polar", angle_unit="degrees")
    qt_export_figure({
        "viewer_type": ScatterViewer,
        "data": data_xyz,
        "tool_id": "save:plotly2d",
        "output_path": output_path,
        "viewer_state": viewer_state,
    })
    return output_path
