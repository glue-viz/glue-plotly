from __future__ import absolute_import, division, print_function

from math import sqrt

from astropy.visualization import (LinearStretch, SqrtStretch, AsinhStretch,
                                   LogStretch, ManualInterval, ContrastBiasStretch)
import numpy as np
from matplotlib.cm import get_cmap
from matplotlib.colors import to_rgb, to_hex, Normalize

from qtpy import compat
from glue.config import viewer_tool, settings, colormaps

from glue.core import DataCollection, Data
from glue.core.subset import RoiSubsetState, RangeSubsetState
from glue.utils import ensure_numerical
from glue.viewers.image.composite_array import COLOR_CONVERTER, STRETCHES
from glue.viewers.image.frb_artist import imshow
from glue.viewers.image.state import ImageLayerState, ImageSubsetLayerState
from glue.viewers.scatter.state import ScatterLayerState

from .. import save_hover

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

from plotly.offline import plot
import plotly.graph_objs as go

DEFAULT_FONT = 'Arial, sans-serif'


def slice_to_bound(slc, size):
    min, max, step = slc.indices(size)
    n = (max - min - 1) // step
    max = min + step * n
    return (min, max, n + 1)


@viewer_tool
class PlotlyImage2DExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotlyimage2d'
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

        width, height = self.viewer.figure.get_size_inches() * self.viewer.figure.dpi

        # set the aspect ratio of the axes, the tick label size, the axis label
        # sizes, and the axes limits
        layout_config = dict(
            margin=dict(r=50, l=50, b=50, t=50),  # noqa
            width=1200,
            height=1200 * height / width,  # scale axis correctly
            paper_bgcolor=settings.BACKGROUND_COLOR,
            plot_bgcolor=settings.BACKGROUND_COLOR,
            showlegend=True
        )

        x_axis = dict(
            title=self.viewer.axes.get_xlabel(),
            titlefont=dict(
                family=DEFAULT_FONT,
                size=2 * self.viewer.axes.xaxis.get_label().get_size(),
                color=settings.FOREGROUND_COLOR
            ),
            showspikes=False,
            linecolor=settings.FOREGROUND_COLOR,
            tickcolor=settings.FOREGROUND_COLOR,
            mirror=True,
            ticks='outside',
            zeroline=False,
            showline=True,
            showgrid=False,
            showticklabels=True,
            tickfont=dict(
                family=DEFAULT_FONT,
                size=1.5 * self.viewer.axes.xaxis.get_ticklabels()[
                    0].get_fontsize(),
                color=settings.FOREGROUND_COLOR),
            range=[self.viewer.axes.get_xlim()[0], self.viewer.axes.get_xlim()[1]],
            # tickmode='array',
            # tickvals=self.viewer.axes.
        )
        y_axis = dict(
            title=self.viewer.axes.get_ylabel(),
            titlefont=dict(
                family=DEFAULT_FONT,
                size=2 * self.viewer.axes.yaxis.get_label().get_size(),
                color=settings.FOREGROUND_COLOR),
            showgrid=False,
            showspikes=False,
            linecolor=settings.FOREGROUND_COLOR,
            tickcolor=settings.FOREGROUND_COLOR,
            zeroline=False,
            mirror=True,
            ticks='outside',
            showline=True,
            range=[self.viewer.axes.get_ylim()[0], self.viewer.axes.get_ylim()[1]],
            # range=[self.viewer.state.y_min, self.viewer.state.y_max],
            showticklabels=True,
            tickfont=dict(
                family=DEFAULT_FONT,
                size=1.5 * self.viewer.axes.yaxis.get_ticklabels()[
                    0].get_fontsize(),
                color=settings.FOREGROUND_COLOR),
        )
        layout_config.update(xaxis=x_axis, yaxis=y_axis)

        layout = go.Layout(**layout_config)

        fig = go.Figure(layout=layout)

        full_view, agg_func, transpose = self.viewer.state.numpy_slice_aggregation_transpose
        x_axis = self.viewer.state.x_att.axis
        y_axis = self.viewer.state.y_att.axis
        full_view[x_axis] = slice(None)
        full_view[y_axis] = slice(None)
        for i in range(self.viewer.state.reference_data.ndim):
            if isinstance(full_view[i], slice):
                full_view[i] = slice_to_bound(full_view[i], self.viewer.state.reference_data.shape[i])

        bg_colors = []
        layers = sorted(self.viewer.layers, key=lambda x: x.zorder)
        for layer in layers:

            layer_state = layer.state

            if not (layer_state.visible and layer.enabled):
                continue

            color = 'gray' if layer_state.color == '0.35' else layer_state.color

            if isinstance(layer_state, ImageLayerState):

                # get image data and scale it down to default size
                # img = layer_state.layer[layer_state.attribute]

                interval = ManualInterval(layer_state.v_min, layer_state.v_max)
                contrast_bias = ContrastBiasStretch(layer_state.contrast, layer_state.bias)
                array = layer.get_image_data
                if callable(array):
                    array = array(bounds=None)
                if array is None:
                    continue

                if np.isscalar(array):
                    array = np.atleast_2d(array)

                img = STRETCHES[layer_state.stretch]()(contrast_bias(interval(array)))
                img[np.isnan(img)] = 0

                # x = layer_state.layer[self.viewer.state.x_att_world]
                # y = layer_state.layer[self.viewer.state.y_att_world]
                # print(self.viewer.state.reference_data[self.viewer.state.x_att_world])

                marker = {}

                # set the opacity
                marker['opacity'] = layer_state.alpha

                # get colors
                colors = {
                    'Red-Blue': 'RdBu',
                    'Gray': 'Greys',
                    'Hot': 'Hot',
                    'Viridis': 'Viridis',
                    'Yellow-Green-Blue': 'YlGnBu',
                    'Yellow-Orange-Red': 'YlOrRd'
                }

                # default colorscale
                colorscale = None
                if layer_state.v_min > layer_state.v_max:
                    cmap = layer_state.cmap.reversed()
                    bounds = [layer_state.v_max, layer_state.v_min]
                else:
                    cmap = layer_state.cmap
                    bounds = [layer_state.v_min, layer_state.v_max]
                if self.viewer.state.color_mode == 'Colormaps':
                    for name, colormap in colormaps.members:
                        if layer_state.cmap == colormap and name in colors:
                            colorscale = colors[name]
                            bg_colors.append([layer_state.alpha, colormap(bounds[0])])
                            break
                    if colorscale is None:
                        color_bounds = STRETCHES[layer_state.stretch]()(contrast_bias(interval(bounds)))
                        colors = [tuple(int(256 * v) for v in cmap(c)) for c in color_bounds]
                        colorstrings = ['rgb{0}'.format(c) for c in colors]
                        colorscale = [[0, colorstrings[0]], [1, colorstrings[1]]]
                        bg_colors.append([layer_state.alpha, cmap(color_bounds[0])])
                else:
                    rgb_color = to_rgb(color)
                    colorscale = [[0, 'rgb(0,0,0)'], [1, 'rgb{0}'.format(tuple(int(256 * v) for v in rgb_color))]]
                    bg_colors.append([layer_state.alpha, [0, 0, 0]])

                # add hover info to layer
                if np.sum(dialog.checked_dictionary[layer_state.layer.label]) == 0:
                    hoverinfo = 'skip'
                    hovertext = None
                else:
                    hoverinfo = 'text'
                    hovertext = ["" for _ in range((layer_state.layer.shape[0]))]
                    for i in range(0, len(layer_state.layer.components)):
                        if dialog.checked_dictionary[layer_state.layer.label][i]:
                            hover_data = layer_state.layer[layer_state.layer.components[i].label]
                            for k in range(0, len(hover_data)):
                                hovertext[k] = (hovertext[k] + "{}: {} <br>"
                                                .format(layer_state.layer.components[i].label,
                                                        hover_data[k]))

                # add layer to dict
                # need to figure out how to get the right tick numbers
                # background color outside of image need to match the cmap max
                image_info = dict(
                    z=img,
                    colorscale=colorscale,
                    hoverinfo=hoverinfo,
                    hovertext=hovertext,
                    name=layer_state.layer.label,
                    opacity=layer_state.alpha,
                    showscale=False,
                    showlegend=True
                )
                if colorscale == 'Greys':
                    image_info.update(reversescale=True)
                fig.add_trace(go.Heatmap(**image_info))

            elif isinstance(layer_state, ImageSubsetLayerState):
                ss = layer.layer.subset_state
                buf = self.viewer.state.reference_data \
                    .compute_fixed_resolution_buffer(full_view,
                                                     target_data=self.viewer.state.reference_data,
                                                     broadcast=False, subset_state=ss)
                if transpose:
                    buf = buf.transpose()

                vf = np.vectorize(int)
                img = vf(buf)
                rgb_color = to_rgb(color)
                colorscale = [[0, 'rgb(0,0,0)'], [1, 'rgb{0}'.format(tuple(int(256 * v) for v in rgb_color))]]
                image_info = dict(
                    z=img,
                    colorscale=colorscale,
                    name=layer_state.layer.label,
                    opacity=layer_state.alpha,
                    showscale=False,
                    showlegend=True
                )
                fig.add_trace(go.Heatmap(**image_info))


            elif isinstance(layer_state, ScatterLayerState):
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
                    s = ensure_numerical(layer_state.layer[layer_state.size_att].ravel())
                    marker['size'] = 25 * (s - layer_state.size_vmin) / (
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
                    hovertext = ["" for _ in range((layer_state.layer.shape[0]))]
                    for i in range(0, len(layer_state.layer.components)):
                        if dialog.checked_dictionary[layer_state.layer.label][i]:
                            hover_data = layer_state.layer[layer_state.layer.components[i].label]
                            for k in range(0, len(hover_data)):
                                hovertext[k] = (hovertext[k] + "{}: {} <br>"
                                                .format(layer_state.layer.components[i].label,
                                                        hover_data[k]))

                # add layer to axesdict
                scatter_info = dict(
                    mode='markers',
                    marker=marker,
                    hoverinfo=hoverinfo,
                    hovertext=hovertext,
                    name=layer_state.layer.label
                )
                scatter_info.update(x=x, y=y)
                fig.add_scatter(**scatter_info)

        # The background color is a weighted sum of the bottom (0) color
        # of the colorscales for each of the image layers
        alpha_sum = sum(x[0] for x in bg_colors)
        bg_color = []
        for i in range(3):
            s = sum((color[i] ** 2) * (w / alpha_sum) for w, color in bg_colors)
            bg_color.append(sqrt(s))
        fig.update_layout(plot_bgcolor=to_hex(bg_color))

        plot(fig, filename=filename, auto_open=False)
