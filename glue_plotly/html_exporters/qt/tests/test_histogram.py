import pytest

from glue.core import Data

pytest.importorskip("glue_qt")

from glue_qt.viewers.histogram import HistogramViewer

from .helpers import qt_export_smoketest


def test_smoketest_histogram(tmpdir):
    data = Data(x=[40, 41, 37, 63, 78, 35, 19, 100, 35, 86, 84, 99,
                   87, 56, 2, 71, 22, 36, 10, 1, 26, 70, 45, 20, 8],
                   label="d1")
    output_path = tmpdir.join("smoketest_qt_histogram.html").strpath
    qt_export_smoketest(HistogramViewer, data, "save:plotlyhist", output_path)
