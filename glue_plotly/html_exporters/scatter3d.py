from __future__ import absolute_import, division, print_function

import numpy as np
import matplotlib.colors as colors
from matplotlib.colors import Normalize

from qtpy import compat
from glue.config import viewer_tool

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

from plotly.offline import plot
import plotly.graph_objs as go


DEFAULT_FONT = 'Arial, sans-serif'


@viewer_tool
class PlotlyScatter3DStaticExport(Tool):

    icon = PLOTLY_LOGO
    tool_id = 'save:plotly3d'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        filename, _ = compat.getsavefilename(
            parent=self.viewer, basedir="plot.html")

        # when vispy viewer is in "native aspect ratio" mode, scale axes size by data
        if self.viewer.state.native_aspect:
            width = self.viewer.state.x_max-self.viewer.state.x_min
            height = self.viewer.state.y_max-self.viewer.state.y_min
            depth = self.viewer.state.z_max-self.viewer.state.z_min

        # otherwise, set all axes to be equal size
        else:
            width = 1200  # this 1200 size is arbitrary, could change to any width; just need to scale rest accordingly
            height = 1200
            depth = 1200

        # set the aspect ratio of the axes, the tick label size, the axis label sizes, and the axes limits
        layout = go.Layout(
            margin=dict(r=50, l=50, b=50, t=50),  # noqa
            width=1200,
            scene=dict(
                xaxis=dict(
                    title=self.viewer.state.x_att.label,
                    titlefont=dict(
                        family=DEFAULT_FONT,
                        size=20,
                        color='black'
                    ),
                    showticklabels=True,
                    tickfont=dict(
                        family=DEFAULT_FONT,
                        size=12,
                        color='black'),
                    range=[self.viewer.state.x_min, self.viewer.state.x_max]),
                yaxis=dict(
                    title=self.viewer.state.y_att.label,
                    titlefont=dict(
                        family=DEFAULT_FONT,
                        size=20,
                        color='black'),
                    range=[self.viewer.state.y_min, self.viewer.state.y_max],
                    showticklabels=True,
                    tickfont=dict(
                        family=DEFAULT_FONT,
                        size=12,
                        color='black'),
                ),
                zaxis=dict(
                    title=self.viewer.state.z_att.label,
                    titlefont=dict(
                        family=DEFAULT_FONT,
                        size=20,
                        color='black'),
                    range=[self.viewer.state.z_min, self.viewer.state.z_max],
                    showticklabels=True,
                    tickfont=dict(
                        family=DEFAULT_FONT,
                        size=12,
                        color='black'),
                ),
                aspectratio=dict(x=1*self.viewer.state.x_stretch, y=height/width *
                                 self.viewer.state.y_stretch, z=depth/width*self.viewer.state.z_stretch),
                aspectmode='manual',),
        )

        fig = go.Figure(layout=layout)

        # only show if visible in viewer
        for layer_state in self.viewer.state.layers:

            if layer_state.visible:

                marker = {}

                try:
                    x = layer_state.layer[self.viewer.state.x_att]
                    y = layer_state.layer[self.viewer.state.y_att]
                    z = layer_state.layer[self.viewer.state.z_att]
                except Exception:
                    print("Cannot visualize layer {}. This layer depends on "
                          "attributes that cannot be derived for the underlying "
                          "dataset.".format(layer_state.layer.label))
                    continue

                # set all points to be the same color
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

                    # most matplotlib colormaps aren't recognized by plotly, so we convert manually to a hex code
                    rgba_list = [cmap(
                        norm(point)) for point in layer_state.layer[layer_state.cmap_attribute].copy()]
                    rgb_str = [r'{}'.format(colors.rgb2hex(
                        (rgba[0], rgba[1], rgba[2]))) for rgba in rgba_list]
                    marker['color'] = rgb_str

                # set all points to be the same size, with some arbitrary scaling
                if layer_state.size_mode == 'Fixed':
                    marker['size'] = layer_state.size

                # scale size of points by some attribute
                else:
                    marker['size'] = 25 * (layer_state.layer[layer_state.size_attribute] -
                                           layer_state.size_vmin) / (layer_state.size_vmax - layer_state.size_vmin)
                    marker['sizemin'] = 1
                    marker['size'][np.isnan(marker['size'])] = 0
                    marker['size'][marker['size'] < 0] = 0

                # set the opacity
                marker['opacity'] = layer_state.alpha
                marker['line'] = dict(width=0)

                # add layer to axes
                fig.add_scatter3d(x=x, y=y, z=z,
                                  mode='markers',
                                  marker=marker,
                                  name=layer_state.layer.label)

        plot(fig, filename=filename, auto_open=False)
