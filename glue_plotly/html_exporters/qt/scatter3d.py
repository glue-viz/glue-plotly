from __future__ import absolute_import, division, print_function

import numpy as np

from qtpy import compat
from qtpy.QtWidgets import QDialog

from glue.config import viewer_tool, settings
from glue.core import DataCollection, Data
from glue_qt.core.dialogs import warn
from glue_qt.utils import messagebox_on_error
from glue_qt.utils.threading import Worker
from glue_qt.viewers.common.tool import Tool

from glue_plotly import PLOTLY_ERROR_MESSAGE, PLOTLY_LOGO
from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.scatter3d import layout_config, traces_for_layer
from ... import save_hover, export_dialog

from plotly.offline import plot
import plotly.graph_objs as go

DEFAULT_FONT = 'Arial, sans-serif'
settings.add('SHOW_WARN_PLOTLY_3D_GRAPHICS_DIFFERENT', True)


@viewer_tool
class PlotlyScatter3DStaticExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotly3d'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    @messagebox_on_error(PLOTLY_ERROR_MESSAGE)
    def _export_to_plotly(self, filename, checked_dictionary):

        config = layout_config(self.viewer.state)
        layout = go.Layout(**config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        for layer in layers:
            traces = traces_for_layer(self.viewer.state, layer.state,
                                      hover_data=checked_dictionary[layer.state.layer.label],
                                      add_data_label=add_data_label)
            for trace in traces:
                fig.add_trace(trace)

        plot(fig, filename=filename, auto_open=False)

    def activate(self):

        # grab hover info
        dc_hover = DataCollection()

        for layer in self.viewer.layers:
            layer_state = layer.state
            if layer_state.visible and layer.enabled:
                data = Data(label=layer_state.layer.label)
                for component in layer_state.layer.components:
                    data[component.label] = np.ones(10)
                dc_hover.append(data)

        checked_dictionary = {}

        # figure out which hover info user wants to display
        for layer in self.viewer.layers:
            layer_state = layer.state
            if layer_state.visible and layer.enabled:
                checked_dictionary[layer_state.layer.label] = np.zeros((len(layer_state.layer.components))).astype(bool)

        proceed = warn('Scatter 3d plotly may look different',
                       'Plotly and Matlotlib graphics differ and your graph may look different when exported. Do you '
                       'want to proceed?',
                       default='Cancel', setting='SHOW_WARN_PLOTLY_3D_GRAPHICS_DIFFERENT')
        if not proceed:
            return

        dialog = save_hover.SaveHoverDialog(data_collection=dc_hover, checked_dictionary=checked_dictionary)
        result = dialog.exec_()
        if result == QDialog.Rejected:
            return

        # query filename
        filename, _ = compat.getsavefilename(
            parent=self.viewer, basedir="plot.html")
        if not filename:
            return

        worker = Worker(self._export_to_plotly, filename, checked_dictionary)
        exp_dialog = export_dialog.ExportDialog(parent=self.viewer)
        worker.result.connect(exp_dialog.close)
        worker.error.connect(exp_dialog.close)
        worker.start()
        exp_dialog.exec_()
