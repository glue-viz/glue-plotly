from __future__ import absolute_import, division, print_function

import numpy as np

from qtpy import compat
from glue.config import viewer_tool
from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

from plotly.offline import plot
import plotly.graph_objs as go


@viewer_tool
class PlotlyScatter2DStaticExport(Tool):

    icon = PLOTLY_LOGO
    tool_id = 'save:plotly'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")

        fig = go.Figure(layout={'width': 800, 'height': 600})

        for layer_state in self.viewer.state.layers:

            marker = {}

            x = layer_state.layer[self.viewer.state.x_att]
            y = layer_state.layer[self.viewer.state.y_att]

            if layer_state.cmap_mode == 'Fixed':
                marker['color'] = layer_state.color
            else:
                marker['color'] = layer_state.layer[layer_state.cmap_att].copy()
                marker['cmin'] = layer_state.cmap_vmin
                marker['cmax'] = layer_state.cmap_vmin
                marker['colorscale'] = layer_state.cmap.name.upper()

            if layer_state.size_mode == 'Fixed':
                marker['size'] = layer_state.size
            else:
                marker['size'] = 20 * (layer_state.layer[layer_state.size_att] - layer_state.size_vmin) / (layer_state.size_vmax - layer_state.size_vmin)
                marker['sizemin'] = 5

            marker['size'][np.isnan(marker['size'])] = 0
            marker['size'][marker['size'] < 0] = 0
            marker['color'][np.isnan(marker['color'])] = -np.inf

            marker['opacity'] = layer_state.alpha

            fig.add_scatter(x=x, y=y,
                            mode='markers',
                            marker=marker)

        plot(fig, filename=filename, auto_open=False)
