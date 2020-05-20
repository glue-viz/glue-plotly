from __future__ import absolute_import, division, print_function

import numpy as np
import matplotlib.colors as colors
from matplotlib.colors import Normalize

from qtpy import compat
from glue.config import viewer_tool

from glue.core import DataCollection, Data

from .. import save_hover

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

from plotly.offline import plot
import plotly.graph_objs as go


DEFAULT_FONT = 'Arial, sans-serif'


@viewer_tool
class PlotlyScatter2DStaticExport(Tool):

    icon = PLOTLY_LOGO
    tool_id = 'save:plotly2d'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        # grab hover info
        dc_hover = DataCollection()
        for layer in self.viewer.layers:
            layer_state = layer.state
            if layer_state.visible and layer.enabled:
                data = Data(label=layer_state.layer.label)
                for component in layer_state.layer.components:
                    data[component.label] = np.ones(10)
                dc_hover.append(data)

        checked_dictionary = {}

        # figure out which hover info user wants to display
        for layer in self.viewer.layers:
            layer_state = layer.state
            if layer_state.visible and layer.enabled:
                checked_dictionary[layer_state.layer.label] = np.zeros((len(layer_state.layer.components))).astype(bool)

        dialog = save_hover.SaveHoverDialog(data_collection=dc_hover, checked_dictionary=checked_dictionary)
        dialog.exec_()

        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")

        width, height = self.viewer.figure.get_size_inches()*self.viewer.figure.dpi

        # set the aspect ratio of the axes, the tick label size, the axis label
        # sizes, and the axes limits
        layout = go.Layout(
            margin=dict(r=50, l=50, b=50, t=50),  # noqa
            width=1200,
            height=1200*height/width,  # scale axis correctly
            plot_bgcolor='white',
            xaxis=dict(
                title=self.viewer.axes.get_xlabel(),
                titlefont=dict(
                    family=DEFAULT_FONT,
                    size=2*self.viewer.axes.xaxis.get_label().get_size(),
                    color='black'
                ),
                showspikes=False,
                zerolinecolor='rgb(128,128,128)',
                showticklabels=True,
                tickfont=dict(
                    family=DEFAULT_FONT,
                    size=1.5*self.viewer.axes.xaxis.get_ticklabels()[
                        0].get_fontsize(),
                    color='black'),
                range=[self.viewer.state.x_min, self.viewer.state.x_max]),
            yaxis=dict(
                title=self.viewer.axes.get_ylabel(),
                titlefont=dict(
                    family=DEFAULT_FONT,
                    size=2*self.viewer.axes.yaxis.get_label().get_size(),
                    color='black'),
                showspikes=False,
                gridcolor='rgb(220,220,220)',
                range=[self.viewer.state.y_min, self.viewer.state.y_max],
                showticklabels=True,
                tickfont=dict(
                    family=DEFAULT_FONT,
                    size=1.5*self.viewer.axes.yaxis.get_ticklabels()[
                        0].get_fontsize(),
                    color='black'),
            )
        )

        fig = go.Figure(layout=layout)

        for layer in self.viewer.layers:

            layer_state = layer.state

            if layer_state.visible and layer.enabled:

                x = layer_state.layer[self.viewer.state.x_att]
                y = layer_state.layer[self.viewer.state.y_att]

                marker = {}

                # set all points to be the same color
                if layer_state.cmap_mode == 'Fixed':
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

                    # most matplotlib colormaps aren't recognized by plotly, so we convert manually to a hex code
                    rgba_list = [
                        cmap(norm(point)) for point in layer_state.layer[layer_state.cmap_att].copy()]
                    rgb_str = [r'{}'.format(colors.rgb2hex(
                        (rgba[0], rgba[1], rgba[2]))) for rgba in rgba_list]
                    marker['color'] = rgb_str

                # set all points to be the same size, with some arbitrary scaling
                if layer_state.size_mode == 'Fixed':
                    marker['size'] = layer_state.size

                # scale size of points by some attribute
                else:
                    marker['size'] = 25 * (layer_state.layer[layer_state.size_att] - layer_state.size_vmin) / (
                        layer_state.size_vmax - layer_state.size_vmin)
                    marker['sizemin'] = 1
                    marker['size'][np.isnan(marker['size'])] = 0
                    marker['size'][marker['size'] < 0] = 0

                # set the opacity
                marker['opacity'] = layer_state.alpha

                # remove default white border around points
                marker['line'] = dict(width=0)

                # add hover info to layer

                if np.sum(dialog.checked_dictionary[layer_state.layer.label]) == 0:
                    hoverinfo = 'skip'
                    hovertext = None
                else:
                    hoverinfo = 'text'
                    hovertext = ["" for i in range((layer_state.layer.shape[0]))]
                    for i in range(0, len(layer_state.layer.components)):
                        if dialog.checked_dictionary[layer_state.layer.label][i]:
                            hover_data = layer_state.layer[layer_state.layer.components[i].label]
                            for k in range(0, len(hover_data)):
                                hovertext[k] = (hovertext[k] + "{}: {} <br>"
                                                .format(layer_state.layer.components[i].label,
                                                        hover_data[k]))

                # add layer to axes
                fig.add_scatter(x=x, y=y,
                                mode='markers',
                                marker=marker,
                                hoverinfo=hoverinfo,
                                hovertext=hovertext,
                                name=layer_state.layer.label)

        plot(fig, filename=filename, auto_open=False)
