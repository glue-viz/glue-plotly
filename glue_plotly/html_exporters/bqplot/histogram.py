from glue.config import viewer_tool

from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.histogram import layout_config, traces_for_layer

from plotly.offline import plot
import plotly.graph_objs as go

from .base import PlotlyBaseBqplotExport


@viewer_tool
class PlotlyHistogramBqplotExport(PlotlyBaseBqplotExport):
    tool_id = 'save:bqplot_plotlyhist'

    def save_figure(self, filepath):

        if not filepath:
            return

        config = layout_config(self.viewer, bargap=0.1)
        layout = go.Layout(**config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        for layer in layers:
            traces = traces_for_layer(self.viewer.state, layer.state, add_data_label=add_data_label)
            fig.add_traces(traces)

        plot(fig, include_mathjax='cdn', filename=filepath, auto_open=False)
