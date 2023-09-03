from glue.config import viewer_tool
from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO
from glue_plotly.common.common import data_count, layers_to_export
from glue_plotly.common.scatter2d import rectilinear_layout_config, traces_for_layer

from plotly.offline import plot
import plotly.graph_objs as go


@viewer_tool
class PlotlyScatter2DBqplotExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:bqplot_plotly2d'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        filename = "plot.html"  # TODO: Add a way to select this

        if not filename:
            return

        layout_config = rectilinear_layout_config(self.viewer)

        layout = go.Layout(**layout_config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        for layer in layers:
            traces = traces_for_layer(self.viewer, layer.state, add_data_label=add_data_label)
            fig.add_traces(traces)

        plot(fig, filename=filename, auto_open=False)