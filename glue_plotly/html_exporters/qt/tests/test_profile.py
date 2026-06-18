import pytest

from glue.core import Data

pytest.importorskip("glue_qt")

from glue_qt.viewers.profile import ProfileViewer

from glue_plotly.tests.helpers import html_screenshot_test

from .helpers import qt_export_figure


@html_screenshot_test
def test_profile(tmp_path, page):
    data = Data(x=[40, 41, 37, 63, 78, 35, 19, 100, 35, 86, 84, 99,
                   87, 56, 2, 71, 22, 36, 10, 1, 26, 70, 45, 20, 8],
                   label="d1")
    output_path = str(tmp_path / "smoketest_qt_profile.html")
    qt_export_figure({
       "viewer_type": ProfileViewer,
        "data": data,
        "tool_id": "save:plotlyprofile",
        "output_path": output_path,
    })
    return output_path
