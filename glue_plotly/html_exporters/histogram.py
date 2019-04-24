from __future__ import absolute_import, division, print_function

import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize


from qtpy import compat
from glue.config import viewer_tool
from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

from plotly.offline import plot
import plotly.graph_objs as go


DEFAULT_FONT = 'Arial, sans-serif'


@viewer_tool
class PlotlyHistogramStaticExport(Tool):

    icon = PLOTLY_LOGO
    tool_id = 'save:plotly'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        filename, _ = compat.getsavefilename(
            parent=self.viewer, basedir="plot.html")

        width, height = self.viewer.figure.get_size_inches() * self.viewer.figure.dpi

        layout = go.Layout(
            barmode='overlay',
            margin=dict(r=50, l=50, b=50, t=50),
            width=1200,
            height=1200 * height / width,
            xaxis=dict(
                title=self.viewer.axes.get_xlabel(),
                titlefont=dict(
                    family=DEFAULT_FONT,
                    size=self.viewer.axes.xaxis.get_label().get_size(),
                    color='black'
                ),
                showticklabels=True,
                tickfont=dict(
                    family=DEFAULT_FONT,
                    size=self.viewer.axes.xaxis.get_ticklabels()[
                        0].get_fontsize(),
                    color='black'),
                range=[self.viewer.state.x_min, self.viewer.state.x_max]),
            yaxis=dict(
                title=self.viewer.axes.get_xlabel(),
                titlefont=dict(
                    family=DEFAULT_FONT,
                    size=self.viewer.axes.yaxis.get_label().get_size(),
                    color='black'),
                range=[self.viewer.state.y_min, self.viewer.state.y_max],
                showticklabels=True,
                tickfont=dict(
                    family=DEFAULT_FONT,
                    size=self.viewer.axes.yaxis.get_ticklabels()[
                        0].get_fontsize(),
                    color='black'),
            )
        )

        fig = go.Figure(layout=layout)

        for layer_state in self.viewer.state.layers:

            if layer_state.visible is True:

                marker = {}

                x = layer_state.layer[self.viewer.state.x_att]

                if layer_state.color_mode == 'Fixed':
                    if layer_state.color != '0.35':
                        marker['color'] = layer_state.color
                    else:
                        marker['color'] = 'gray'

            # color by some attribute
            else:
                if layer_state.cmap_vmin > layer_state.cmap_vmax:
                    cmap = layer_state.cmap.reversed()
                    norm = Normalize(
                        vmin=layer_state.cmap_vmax, vmax=layer_state.cmap_vmin)
                else:
                    cmap = layer_state.cmap
                    norm = Normalize(
                        vmin=layer_state.cmap_vmin, vmax=layer_state.cmap_vmax)

                # most matplotlib colormaps aren't recognized by plotly, so we
                # convert manually to a hex code
                rgba_list = [
                    cmap(norm(point)) for point in layer_state.layer[layer_state.cmap_att].copy()]
                rgb_str = [r'{}'.format(colors.rgb2hex(
                    (rgba[0], rgba[1], rgba[2]))) for rgba in rgba_list]
                marker['color'] = rgb_str

            # set the opacity
            marker['opacity'] = layer_state.alpha

            # add layer to axes
            fig.add_histogram(x=x,
                              marker=marker,
                              name=layer_state.layer.label)

        plot(fig, filename=filename, auto_open=False)
