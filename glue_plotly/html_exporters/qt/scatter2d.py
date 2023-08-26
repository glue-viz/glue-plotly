from __future__ import absolute_import, division, print_function

import numpy as np

from qtpy import compat
from qtpy.QtWidgets import QDialog

from glue.config import viewer_tool, settings
from glue.core import DataCollection, Data
from glue.viewers.common.tool import Tool
from glue_qt.core.dialogs import warn
from glue_qt.utils import messagebox_on_error

from ... import save_hover

from glue_plotly import PLOTLY_ERROR_MESSAGE, PLOTLY_LOGO
from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.scatter2d import polar_layout_config_from_mpl, rectilinear_layout_config, \
    traces_for_layer

from plotly.offline import plot
import plotly.graph_objs as go

DEFAULT_FONT = 'Arial, sans-serif'

SHOW_PLOTLY_VECTORS_2D_DIFFERENT = 'SHOW_PLOTLY_2D_VECTORS_DIFFERENT'
settings.add(SHOW_PLOTLY_VECTORS_2D_DIFFERENT, True)


@viewer_tool
class PlotlyScatter2DStaticExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotly2d'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    @messagebox_on_error(PLOTLY_ERROR_MESSAGE)
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

        dialog = save_hover.SaveHoverDialog(data_collection=dc_hover, checked_dictionary=checked_dictionary)
        result = dialog.exec_()
        if result == QDialog.Rejected:
            return

        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")
        if not filename:
            return

        rectilinear = getattr(self.viewer.state, 'using_rectilinear', True)
        polar = getattr(self.viewer.state, 'using_polar', False)

        if polar:
            layout_config = polar_layout_config_from_mpl(self.viewer)
        else:
            layout_config = rectilinear_layout_config(self.viewer)

        if rectilinear:
            need_vectors = any(layer.state.vector_visible and layer.state.vector_scaling > 0.1
                               for layer in self.viewer.layers)
            if need_vectors:
                proceed = warn('Arrows may look different',
                               'Plotly and Matlotlib vector graphics differ and your graph may look different '
                               'when exported. Do you want to proceed?',
                               default='Cancel', setting=SHOW_PLOTLY_VECTORS_2D_DIFFERENT)
                if not proceed:
                    return

        layout = go.Layout(**layout_config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        for layer in layers:
            traces = traces_for_layer(self.viewer,
                                      layer.state,
                                      hover_data=checked_dictionary[layer.state.layer.label],
                                      add_data_label=add_data_label)
            fig.add_traces(traces)

        plot(fig, filename=filename, auto_open=False)
