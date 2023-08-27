from glue.config import viewer_tool
from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO
from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.histogram import layout_config, traces_for_layer

from plotly.offline import plot
import plotly.graph_objs as go


@viewer_tool
class PlotlyHistogramBqplotExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:bqplot_plotlyhist'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        filename = "plot.html"

        if not filename:
            return

        config = layout_config(self.viewer, bargap=0.1)
        layout = go.Layout(**config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        for layer in layers:
            traces = traces_for_layer(self.viewer.state, layer.state, add_data_label=add_data_label)
            fig.add_traces(traces)

        plot(fig, include_mathjax='cdn', filename=filename, auto_open=False)

