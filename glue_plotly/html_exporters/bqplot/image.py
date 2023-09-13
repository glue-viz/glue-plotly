from glue.config import viewer_tool

from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.image import axes_data_from_bqplot, layout_config, traces

from plotly.offline import plot
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .base import PlotlyBaseBqplotExport


@viewer_tool
class PlotlyImageBqplotExport(PlotlyBaseBqplotExport):
    tool_id = 'save:bqplot_plotlyimage2d'

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

        if secondary_x or secondary_y:
            fig = make_subplots(specs=[[{"secondary_y": True}]], horizontal_spacing=0, vertical_spacing=0)
            fig.update_layout(**config)
        else:
            layout = go.Layout(**config)
            fig = go.Figure(layout=layout)

        traces_to_add = traces(self.viewer,
                               secondary_x=secondary_x,
                               secondary_y=secondary_y,
                               add_data_label=add_data_label)
        fig.add_traces(traces_to_add)

        plot(fig, include_mathjax='cdn', filename=filepath, auto_open=False)
