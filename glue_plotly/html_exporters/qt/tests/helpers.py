import os
from unittest.mock import patch

import pytest

pytest.importorskip("glue_qt")

from glue_qt.app import GlueApplication
from qtpy.QtWidgets import QMessageBox

from glue_plotly.html_exporters.qt.save_hover import SaveHoverDialog
from glue_plotly.sort_components import SortComponentsDialog
from glue_plotly.volume_options import VolumeOptionsDialog


def auto_accept_selectdialog():
    def exec_replacement(dialog):
        dialog.select_all()
        dialog.accept()
    return exec_replacement


def auto_accept_messagebox():
    def exec_replacement(box):
        box.accept()
    return exec_replacement


def export_figure(self, tmpdir, output_filename):
    output_path = tmpdir.join(output_filename).strpath
    with patch("qtpy.compat.getsavefilename") as fd:
        fd.return_value = output_path, "html"
        with patch.object(SaveHoverDialog, "exec_",
                          self.auto_accept_selectdialog()), \
             patch.object(SortComponentsDialog, "exec_",
                          self.auto_accept_selectdialog()), \
             patch.object(VolumeOptionsDialog, "exec_",
                          self.auto_accept_messagebox()), \
             patch.object(QMessageBox, "exec_",
                          self.auto_accept_messagebox()):
            self.tool.activate()
    return output_path


def qt_export_smoketest(options):
    app = GlueApplication()
    data = options["data"]
    app.session.data_collection.append(data)
    viewer = app.new_data_viewer(options["viewer_type"], 
                                 data=data, 
                                 state=options.get("viewer_state", None))
    tool_id = options["tool_id"]
    for subtool in viewer.toolbar.tools["save"].subtools:
        if subtool.tool_id = tool_id:
            tool = subtool
            break
    else:
        msg = f"Could not find {tool_id} tool in viewer"
        raise ValueError(msg)

    output_path = options["output_path"]
    with patch("qtpy.compat.getsavefilename") as fd:
        fd.return_value = output_path, "html"
        with patch.object(SaveHoverDialog, "exec_",
                          auto_accept_selectdialog()), \
             patch.object(SortComponentsDialog, "exec_",
                          auto_accept_selectdialog()), \
             patch.object(VolumeOptionsDialog, "exec_",
                          auto_accept_messagebox()), \
             patch.object(QMessageBox, "exec_",
                          auto_accept_messagebox()):
            tool.activate()

    assert os.path.exists(output_path)
