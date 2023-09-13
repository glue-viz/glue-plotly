from glue.config import viewer_tool

from glue_plotly.common.common import data_count, layers_to_export
from glue_plotly.common.scatter2d import rectilinear_layout_config, traces_for_layer

from plotly.offline import plot
import plotly.graph_objs as go

from .base import PlotlyBaseBqplotExport


@viewer_tool
class PlotlyScatter2DBqplotExport(PlotlyBaseBqplotExport):
    tool_id = 'save:bqplot_plotly2d'

    def save_figure(self, filepath):

        if not filepath:
            return

        layout_config = rectilinear_layout_config(self.viewer)

        layout = go.Layout(**layout_config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        for layer in layers:
            traces = traces_for_layer(self.viewer, layer.state, add_data_label=add_data_label)
            fig.add_traces(traces)

        plot(fig, filename=filepath, auto_open=False)
