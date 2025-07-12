import plotly.graph_objs as go
from IPython.display import display
from plotly.offline import plot

from glue.config import viewer_tool
from glue_plotly.common.base_3d import layout_config
from glue_plotly.common.common import data_count, layers_to_export
from glue_plotly.common.scatter3d import traces_for_layer
from glue_plotly.html_exporters.hover_utils import hover_data_collection_for_viewer
from glue_plotly.html_exporters.jupyter.save_hover import JupyterSaveHoverDialog
from glue_plotly.jupyter_base_export_tool import JupyterBaseExportTool


@viewer_tool
class PlotlyScatter3DStaticExport(JupyterBaseExportTool):
    tool_id = "save:jupyter_plotly3dscatter"

    def activate(self):
        done = False

        def on_cancel():
            nonlocal done
            done = True

        dc_hover = hover_data_collection_for_viewer(self.viewer)
        self.save_hover_dialog = \
            JupyterSaveHoverDialog(data_collection=dc_hover,
                                   checked_dictionary=None,
                                   display=True,
                                   on_cancel=on_cancel,
                                   on_export=self.open_file_dialog)
        with self.viewer.output_widget:
            display(self.save_hover_dialog)

    def save_figure(self, filepath):

        if not filepath:
            return

        config = layout_config(self.viewer.state)
        layout = go.Layout(**config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        checked_dictionary = self.save_hover_dialog.checked_dictionary \
                             if hasattr(self, "save_hover_dialog") \
                             else None
        for layer in layers:
            hover_data = checked_dictionary[layer.layer.label] \
                    if checked_dictionary is not None \
                    else None
            traces = traces_for_layer(self.viewer.state,
                                      layer.state,
                                      hover_data=hover_data,
                                      add_data_label=add_data_label)
            for trace in traces:
                fig.add_trace(trace)

        plot(fig, filename=filepath, auto_open=False)
