from qtpy import compat

from glue.config import viewer_tool
from glue_qt.viewers.common.tool import Tool
from glue_qt.utils import messagebox_on_error

from glue_plotly import PLOTLY_ERROR_MESSAGE, PLOTLY_LOGO
from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.dendrogram import layout_config_from_mpl, trace_for_layer

from plotly.offline import plot
import plotly.graph_objs as go


@viewer_tool
class PlotlyDendrogramStaticExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotlydendro'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    @messagebox_on_error(PLOTLY_ERROR_MESSAGE)
    def activate(self):

        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")
        if not filename:
            return

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1

        config = layout_config_from_mpl(self.viewer)
        layout = go.Layout(**config)
        fig = go.Figure(layout=layout)

        for layer in layers:
            data = layer.mpl_artists[0].get_xydata()
            trace = trace_for_layer(layer.state, data, add_data_label=add_data_label)
            fig.add_trace(trace)

        plot(fig, filename=filename, auto_open=False)
