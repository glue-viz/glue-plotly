import plotly.graph_objs as go
from plotly.offline import plot

from glue.config import viewer_tool
from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.profile import layout_config, traces_for_layer
from glue_plotly.jupyter_base_export_tool import JupyterBaseExportTool


@viewer_tool
class PlotlyProfileBqplotExport(JupyterBaseExportTool):
    tool_id = "save:bqplot_plotlyprofile"

    def save_figure(self, filepath):
        if not filepath:
            return

        config = layout_config(self.viewer)
        layout = go.Layout(**config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        for layer in layers:
            traces = traces_for_layer(self.viewer.state,
                                      layer.state,
                                      add_data_label=add_data_label)
            fig.add_traces(traces)

        plot(fig, include_mathjax="cdn", filename=filepath, auto_open=False)
