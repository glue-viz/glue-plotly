import pytest

from glue.core import Data

pytest.importorskip("glue_qt")

from glue_qt.viewers.image.data_viewer import ImageViewer
from numpy import arange, ones

from .helpers import qt_export_smoketest


def test_smoketest_image(tmpdir):
    data = Data(label="d1", x=arange(24).reshape((2, 3, 4)), y=ones((2, 3, 4)))
    output_path = tmpdir.join("smoketest_qt_image.html").strpath
    qt_export_smoketest(ImageViewer, data, "save:plotlyimage2d", output_path)
