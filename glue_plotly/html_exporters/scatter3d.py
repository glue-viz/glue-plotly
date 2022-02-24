from __future__ import absolute_import, division, print_function

import numpy as np
import matplotlib.colors as colors
from matplotlib.colors import Normalize

from qtpy import compat
from glue.config import viewer_tool

from glue.core import DataCollection, Data
from glue.utils import ensure_numerical

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO
from .. import save_hover

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

        # query filename
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

        # check which projection we want to use
        projection_type = "perspective" if self.viewer.state.perspective_view else "orthographic"

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
                    showspikes=False,
                    backgroundcolor='white',
                    gridcolor='rgb(220,220,220)',
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
                    showspikes=False,
                    backgroundcolor='white',
                    gridcolor='rgb(220,220,220)',
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
                    showspikes=False,
                    backgroundcolor='white',
                    gridcolor='rgb(220,220,220)',
                    range=[self.viewer.state.z_min, self.viewer.state.z_max],
                    showticklabels=True,
                    tickfont=dict(
                        family=DEFAULT_FONT,
                        size=12,
                        color='black'),
                ),
                camera=dict(
                    projection=dict(
                        type=projection_type
                    )
                ),
                aspectratio=dict(x=1*self.viewer.state.x_stretch, y=height/width *
                                 self.viewer.state.y_stretch, z=depth/width*self.viewer.state.z_stretch),
                aspectmode='manual',),
        )

        fig = go.Figure(layout=layout)

        for layer in self.viewer.layers:

            layer_state = layer.state

            if layer_state.visible and layer.enabled:

                x = layer_state.layer[self.viewer.state.x_att]
                y = layer_state.layer[self.viewer.state.y_att]
                z = layer_state.layer[self.viewer.state.z_att]

                marker = {}

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
                    s = ensure_numerical(layer_state.layer[layer_state.size_attribute].ravel())
                    marker['size'] = 25 * (s - layer_state.size_vmin) / (
                        layer_state.size_vmax - layer_state.size_vmin)
                    marker['sizemin'] = 1
                    marker['size'][np.isnan(marker['size'])] = 0
                    marker['size'][marker['size'] < 0] = 0

                # set the opacity
                marker['opacity'] = layer_state.alpha
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
                fig.add_scatter3d(x=x, y=y, z=z,
                                  mode='markers',
                                  marker=marker,
                                  hoverinfo=hoverinfo,
                                  hovertext=hovertext,
                                  name=layer_state.layer.label)

        plot(fig, filename=filename, auto_open=False)
