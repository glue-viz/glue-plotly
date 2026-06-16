import pytest

from glue.core import Data
from glue.tests.helpers import make_skipper

pytest.importorskip("glue_qt.plugins.dendro_viewer.data_viewer")

from glue_qt.plugins.dendro_viewer.data_viewer import DendrogramViewer

from .helpers import qt_export_smoketest

NUMPY_LT_2, requires_numpy_lt2 = make_skipper("numpy", version="2.0", skip_if="ge")


def test_smoketest_dendrogram(tmpdir):
    data = Data(label="dendrogram",
                parent=[-1, 0, 1, 1],
                height=[1.3, 2.2, 3.2, 4.4])
    output_path = tmpdir.join("smoketest_qt_dendro.html").strpath
    qt_export_smoketest({
        "viewer_type": DendrogramViewer,
        "data": data,
        "tool_id": "save:plotlydendro",
        "output_path": output_path,
    })
