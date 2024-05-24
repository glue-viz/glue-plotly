from qtpy import compat
from qtpy.QtWidgets import QDialog

from glue.config import viewer_tool
from glue_qt.utils import messagebox_on_error
from glue_qt.utils.threading import Worker
from glue_qt.viewers.common.tool import Tool
from glue_vispy_viewers.scatter.layer_artist import ScatterLayerArtist

from glue_plotly import PLOTLY_ERROR_MESSAGE, PLOTLY_LOGO, export_dialog, volume_options
from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.base_3d import layout_config
from glue_plotly.common.scatter3d import traces_for_layer as scatter3d_traces_for_layer
from glue_plotly.common.volume import traces_for_layer as volume_traces_for_layer

from plotly.offline import plot
import plotly.graph_objs as go


@viewer_tool
class PlotlyVolumeStaticExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotlyvolume'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    @messagebox_on_error(PLOTLY_ERROR_MESSAGE)
    def _export_to_plotly(self, filename, state_dictionary):

        config = layout_config(self.viewer.state)
        layout = go.Layout(**config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        bounds = self.viewer._vispy_widget._multivol._data_bounds
        for layer in layers:
            if isinstance(layer, ScatterLayerArtist):
                traces = scatter3d_traces_for_layer(self.viewer.state, layer.state,
                                                    add_data_label=add_data_label)
            else:
                options = state_dictionary[layer.layer.label]
                count = int(options.isosurface_count)
                traces = volume_traces_for_layer(self.viewer.state, layer.state, bounds,
                                                 isosurface_count=count,
                                                 add_data_label=add_data_label)

            for trace in traces:
                fig.add_trace(trace)

        plot(fig, filename=filename, auto_open=False)

    def activate(self):

        dialog = volume_options.VolumeOptionsDialog(viewer=self.viewer)
        result = dialog.exec_()
        if result == QDialog.Rejected:
            return

        filename, _ = compat.getsavefilename(
            parent=self.viewer, basedir="plot.html")
        if not filename:
            return

        worker = Worker(self._export_to_plotly, filename, dialog.state_dictionary)
        exp_dialog = export_dialog.ExportDialog(parent=self.viewer)
        worker.result.connect(exp_dialog.close)
        worker.error.connect(exp_dialog.close)
        worker.start()
        exp_dialog.exec_()
