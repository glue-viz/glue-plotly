import plotly.graph_objs as go
from IPython.display import display
from plotly.offline import plot

from glue.config import viewer_tool
from glue_plotly.common.common import data_count, layers_to_export
from glue_plotly.common.scatter2d import (
    geo_layout_config,
    geo_ticks,
    polar_layout_config_from_mpl,
    rectilinear_layout_config,
    traces_for_layer,
)
from glue_plotly.html_exporters.hover_utils import hover_data_collection_for_viewer
from glue_plotly.html_exporters.jupyter.save_hover import JupyterSaveHoverDialog
from glue_plotly.jupyter_base_export_tool import JupyterBaseExportTool


@viewer_tool
class PlotlyScatter2DBqplotExport(JupyterBaseExportTool):
    tool_id = "save:bqplot_plotly2d"

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

        rectilinear = getattr(self.viewer.state, "using_rectilinear", True)
        polar = getattr(self.viewer.state, "using_polar", False)

        if rectilinear:
            layout_config = rectilinear_layout_config(self.viewer)
        elif polar:
            layout_config = polar_layout_config_from_mpl(self.viewer)
        else:
            layout_config = geo_layout_config(self.viewer)

        layout = go.Layout(**layout_config)
        fig = go.Figure(layout=layout)

        if not (rectilinear or polar):
            for tick in geo_ticks(self.viewer.state):
                fig.add_trace(tick)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        checked_dictionary = self.save_hover_dialog.checked_dictionary \
                             if hasattr(self, "save_hover_dialog") \
                             else None
        for layer in layers:
            hover_data = checked_dictionary[layer.layer.label] \
                         if checked_dictionary is not None \
                         else None
            traces = traces_for_layer(self.viewer,
                                      layer.state,
                                      hover_data=hover_data,
                                      add_data_label=add_data_label)
            fig.add_traces(traces)

        plot(fig, filename=filepath, auto_open=False)
