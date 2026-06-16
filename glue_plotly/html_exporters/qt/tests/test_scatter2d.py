import os
from unittest.mock import patch

from glue.viewers.scatter.state import ScatterViewerState
import pytest
import numpy as np

from glue.core import Data

pytest.importorskip("glue_qt")

from glue_plotly.tests.helpers import html_screenshot_test
from glue_qt.app import GlueApplication
from glue_qt.viewers.scatter import ScatterViewer

from .helpers import qt_export_smoketest


def test_smoketest_scatter2d(tmpdir, data_xyz):
    output_path = tmpdir.join("smoketest_qt_scatter2d_default.html").strpath
    viewer_state = ScatterViewerState(plot_mode="rectilinear")
    qt_export_smoketest({
        "viewer_type": ScatterViewer, 
        "data": data_xyz, 
        "tool_id": "save:plotly2d", 
        "output_path": output_path,
        "viewer_state": viewer_state,
    })


def test_smoketest_scatter2d_polar_radians(tmpdir, data_xyz):
    output_path = tmpdir.join("smoketest_qt_scatter2d_polar_radians.html").strpath
    viewer_state = ScatterViewerState(plot_mode="polar", angle_unit="radians")
    qt_export_smoketest({
        "viewer_type": ScatterViewer, 
        "data": data_xyz, 
        "tool_id": "save:plotly2d", 
        "output_path": output_path,
        "viewer_state": viewer_state,
    })


def test_smoketest_scatter2d_polar_degrees(tmpdir, data_xyz):
    output_path = tmpdir.join("smoketest_qt_scatter2d_polar_degrees.html").strpath
    viewer_state = ScatterViewerState(plot_mode="polar", angle_unit="degrees")
    qt_export_smoketest({
        "viewer_type": ScatterViewer, 
        "data": data_xyz, 
        "tool_id": "save:plotly2d", 
        "output_path": output_path,
        "viewer_state": viewer_state,
    })


