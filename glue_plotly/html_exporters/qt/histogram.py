
import plotly.graph_objs as go
from glue_qt.utils import messagebox_on_error
from glue_qt.viewers.common.tool import Tool
from plotly.offline import plot
from qtpy import compat

from glue.config import viewer_tool
from glue_plotly import PLOTLY_ERROR_MESSAGE, PLOTLY_LOGO
from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.histogram import layout_config_from_mpl, traces_for_layer

DEFAULT_FONT = "Arial, sans-serif"


@viewer_tool
class PlotlyHistogram1DExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = "save:plotlyhist"
    action_text = "Save Plotly HTML page"
    tool_tip = "Save Plotly HTML page"

    @messagebox_on_error(PLOTLY_ERROR_MESSAGE)
    def activate(self):
        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")
        if not filename:
            return

        config = layout_config_from_mpl(self.viewer)
        layout = go.Layout(**config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        for layer in layers:
            traces = traces_for_layer(self.viewer.state, layer.state,
                                      add_data_label=add_data_label)
            for trace in traces:
                fig.add_trace(trace)

        plot(fig, include_mathjax="cdn", filename=filename, auto_open=False)
