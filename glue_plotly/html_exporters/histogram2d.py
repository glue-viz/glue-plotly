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
class PlotlyHistogram2DStaticExport(Tool):

    icon = PLOTLY_LOGO
    tool_id = 'save:plotly2d'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        filename, _ = compat.getsavefilename(
            parent=self.viewer, basedir="plot.html")

        width, height = self.viewer.figure.get_size_inches() * self.viewer.figure.dpi

        layout = go.Layout(
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

                x = layer_state.layer[self.viewer.state.x_att]
                y = layer_state.layer[self.viewer.state.y_att]

                # Not sure if layer_state.color should be used. This is just a
                # placeholder.
                if layer_state.color in ["Blackbody", "Bluered", "Blues", "Earth", "Electric", "Greens", "Greys", "Hot", "Jet",
                                         "Picnic", "Portland", "Rainbow", "RdBu", "Reds", "Viridis", "YlGnBu", "YlOrRd"]:
                    colorscale = layer_state.color
                else:
                    colorscale = 'YlGnBu'

            # add layer to axes
            fig.add_histogram2d(x=x,
                                y=y,
                                colorscale=colorscale,
                                name=layer_state.layer.label)

        plot(fig, filename=filename, auto_open=False)
