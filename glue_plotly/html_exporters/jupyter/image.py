from glue.config import viewer_tool
from IPython.display import display

from plotly.offline import plot
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.image import axes_data_from_bqplot, layers_by_type, layout_config, traces
from glue_plotly.html_exporters.hover_utils import hover_data_collection_for_viewer
from glue_plotly.html_exporters.jupyter.save_hover import JupyterSaveHoverDialog
from glue_plotly.jupyter_base_export_tool import JupyterBaseExportTool


@viewer_tool
class PlotlyImageBqplotExport(JupyterBaseExportTool):
    tool_id = 'save:bqplot_plotlyimage2d'

    def activate(self):
        done = False

        def on_cancel():
            nonlocal done
            done = True

        layers = layers_by_type(self.viewer)
        scatter_layers = layers["scatter"]

        if len(scatter_layers) > 0:
            dc_hover = hover_data_collection_for_viewer(
                self.viewer,
                layer_condition=lambda layer: layer.state.visible and layer.enabled and layer in scatter_layers
            )

            self.save_hover_dialog = \
                JupyterSaveHoverDialog(data_collection=dc_hover,
                                       checked_dictionary=None,
                                       display=True,
                                       on_cancel=on_cancel,
                                       on_export=self.open_file_dialog)

            with self.viewer.output_widget:
                display(self.save_hover_dialog)
        else:
            self.checked_dictionary = None

    def save_figure(self, filepath):

        if not filepath:
            return

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1

        config = layout_config(self.viewer)

        ax = axes_data_from_bqplot(self.viewer)
        config.update(**ax)
        secondary_x = 'xaxis2' in ax
        secondary_y = 'yaxis2' in ax
        config["showlegend"] = len(layers) > 1

        if secondary_x or secondary_y:
            fig = make_subplots(specs=[[{"secondary_y": True}]], horizontal_spacing=0, vertical_spacing=0)
            fig.update_layout(**config)
        else:
            layout = go.Layout(**config)
            fig = go.Figure(layout=layout)

        traces_to_add = traces(self.viewer,
                               secondary_x=secondary_x,
                               secondary_y=secondary_y,
                               hover_selections=self.save_hover_dialog.checked_dictionary,
                               add_data_label=add_data_label)
        fig.add_traces(traces_to_add)

        plot(fig, include_mathjax='cdn', filename=filepath, auto_open=False)
