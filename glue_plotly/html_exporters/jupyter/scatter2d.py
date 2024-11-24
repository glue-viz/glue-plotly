from glue.config import viewer_tool
from IPython.display import display

from plotly.offline import plot
import plotly.graph_objs as go

from glue_plotly.common.common import data_count, layers_to_export
from glue_plotly.common.scatter2d import rectilinear_layout_config, traces_for_layer
from glue_plotly.html_exporters.jupyter.save_hover import JupyterSaveHoverDialog

from ...jupyter_base_export_tool import JupyterBaseExportTool


@viewer_tool
class PlotlyScatter2DBqplotExport(JupyterBaseExportTool):
    tool_id = 'save:bqplot_plotly2d'

    def activate(self):
        done = False

        def on_cancel():
            nonlocal done
            done = True

        self.save_hover_dialog = \
            JupyterSaveHoverDialog(data_collection=self.viewer.state.data_collection,
                                   checked_dictionary=None,
                                   display=True,
                                   on_cancel=on_cancel,
                                   on_export=self.open_file_dialog)
        with self.viewer.output_widget:
            display(self.save_hover_dialog)

    def save_figure(self, filepath):

        if not filepath:
            return

        layout_config = rectilinear_layout_config(self.viewer)

        layout = go.Layout(**layout_config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        for layer in layers:
            traces = traces_for_layer(self.viewer,
                                      layer.state,
                                      hover_data=self.save_hover_dialog.checked_dictionary[layer.state.layer.label],
                                      add_data_label=add_data_label)
            fig.add_traces(traces)

        plot(fig, filename=filepath, auto_open=False)
