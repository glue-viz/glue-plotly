from __future__ import absolute_import, division, print_function

from collections import defaultdict
from math import sqrt

from astropy.visualization import (ManualInterval, ContrastBiasStretch)
import numpy as np
from matplotlib.colors import rgb2hex, to_rgb, to_hex, Normalize

from qtpy import compat
from glue.config import viewer_tool, settings, colormaps

from glue.core import DataCollection, Data
from glue.core.exceptions import IncompatibleAttribute
from glue.utils import ensure_numerical
from glue.viewers.image.pixel_selection_subset_state import PixelSubsetState
from glue.viewers.image.composite_array import COLOR_CONVERTER, STRETCHES
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
    return min, max, n + 1


@viewer_tool
class PlotlyImage2DExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotlyimage2d'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        # grab hover info
        visible_enabled_layers = [layer for layer in self.viewer.layers if layer.state.visible and layer.enabled]
        scatter_layers = [layer for layer in visible_enabled_layers if isinstance(layer.state, ScatterLayerState)]
        if len(scatter_layers) > 0:
            dc_hover = DataCollection()
            for layer in scatter_layers:
                layer_state = layer.state
                if layer_state.visible and layer.enabled:
                    data = Data(label=layer_state.layer.label)
                    for component in layer_state.layer.components:
                        data[component.label] = np.ones(10)
                    dc_hover.append(data)

            checked_dictionary = {}

            # figure out which hover info user wants to display
            for layer in scatter_layers:
                layer_state = layer.state
                if layer_state.visible and layer.enabled:
                    checked_dictionary[layer_state.layer.label] = np.zeros((len(layer_state.layer.components))).astype(
                        bool)

            dialog = save_hover.SaveHoverDialog(data_collection=dc_hover, checked_dictionary=checked_dictionary)
            dialog.exec_()

        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")

        width, height = self.viewer.figure.get_size_inches() * self.viewer.figure.dpi

        xmin, xmax = self.viewer.axes.get_xlim()
        ymin, ymax = self.viewer.axes.get_ylim()

        viewer_state = self.viewer.state

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
            range=[xmin, xmax],
            showticklabels=True,
            tickfont=dict(
                family=DEFAULT_FONT,
                size=1.5 * self.viewer.axes.xaxis.get_ticklabels()[
                    0].get_fontsize(),
                color=settings.FOREGROUND_COLOR)
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
            range=[ymin, ymax],
            showticklabels=True,
            tickfont=dict(
                family=DEFAULT_FONT,
                size=1.5 * self.viewer.axes.yaxis.get_ticklabels()[
                    0].get_fontsize(),
                color=settings.FOREGROUND_COLOR)
        )
        layout_config.update(xaxis=x_axis, yaxis=y_axis)

        layout = go.Layout(**layout_config)

        fig = go.Figure(layout=layout)

        layers_to_add = []
        using_colormaps = viewer_state.color_mode == 'Colormaps'
        has_nonpixel_subset = any(isinstance(layer.state, ImageSubsetLayerState)
                                  and not isinstance(layer.layer.subset_state, PixelSubsetState)
                                  for layer in self.viewer.layers)
        if has_nonpixel_subset:
            full_view, agg_func, transpose = viewer_state.numpy_slice_aggregation_transpose
            x_axis = viewer_state.x_att.axis
            y_axis = viewer_state.y_att.axis
            full_view[x_axis] = slice(None)
            full_view[y_axis] = slice(None)
            for i in range(viewer_state.reference_data.ndim):
                if isinstance(full_view[i], slice):
                    full_view[i] = slice_to_bound(full_view[i], viewer_state.reference_data.shape[i])

        bg_colors = []
        legend_groups = defaultdict(int)
        for layer in visible_enabled_layers:

            layer_state = layer.state
            color = 'gray' if layer_state.color == '0.35' else layer_state.color

            if isinstance(layer_state, ImageLayerState):

                interval = ManualInterval(layer_state.v_min, layer_state.v_max)
                contrast_bias = ContrastBiasStretch(layer_state.contrast, layer_state.bias)
                array = layer.get_image_data
                if callable(array):
                    array = array(bounds=None)
                if array is None:
                    continue

                print(layer.get_image_shape())

                if np.isscalar(array):
                    array = np.atleast_2d(array)

                img = STRETCHES[layer_state.stretch]()(contrast_bias(interval(array)))
                img[np.isnan(img)] = 0

                if layer_state.v_min > layer_state.v_max:
                    cmap = layer_state.cmap.reversed()
                    bounds = [layer_state.v_max, layer_state.v_min]
                else:
                    cmap = layer_state.cmap
                    bounds = [layer_state.v_min, layer_state.v_max]
                mapped_bounds = STRETCHES[layer_state.stretch]()(contrast_bias(interval(bounds)))
                unmapped_space = np.linspace(0, 1, 30)
                mapped_space = np.linspace(mapped_bounds[0], mapped_bounds[1], 30)
                if using_colormaps:
                    color_space = [cmap(b) for b in mapped_space]
                    color_values = [tuple(int(256 * v) for v in p) for p in color_space]
                    colorscale = [[t, 'rgb{0}'.format(c)] for t, c in zip(unmapped_space, color_values)]
                    bg_colors.append([layer_state.alpha, color_space[0]])
                else:
                    rgb_color = to_rgb(color)
                    colorscale = [[u, 'rgb{0}'.format(tuple(int(256 * t * v) for v in rgb_color))] for t, u in zip(mapped_space, unmapped_space)]
                    bg_colors.append([layer_state.alpha, rgb_color])

                image_info = dict(
                    z=img,
                    colorscale=colorscale,
                    hoverinfo='skip',
                    name=layer_state.layer.label,
                    opacity=layer_state.alpha,
                    showscale=False,
                    showlegend=True
                )
                if colorscale == 'Greys':
                    image_info.update(reversescale=True)
                layers_to_add.append([layer.zorder, fig.add_heatmap, image_info])

            elif isinstance(layer_state, ImageSubsetLayerState):
                ss = layer.layer.subset_state
                refdata = viewer_state.reference_data
                if isinstance(ss, PixelSubsetState):
                    try:
                        x, y = ss.get_xy(layer.layer.data, viewer_state.x_att.axis, viewer_state.y_att.axis)
                        label = layer_state.layer.label
                        group = '{0}_{1}'.format(label, legend_groups[label])
                        legend_groups[label] += 1
                        line_data = dict(
                            mode="lines",
                            marker=dict(
                                color=layer_state.color
                            ),
                            opacity=layer_state.alpha * 0.5,
                            name=layer_state.layer.label,
                            legendgroup=group
                        )
                        fig.add_scatter(**line_data, x=[x, x], y=[ymin, ymax], showlegend=True)
                        fig.add_scatter(**line_data, x=[xmin, xmax], y=[y, y], showlegend=False)
                    except IncompatibleAttribute:
                        pass
                else:
                    buf = refdata \
                        .compute_fixed_resolution_buffer(full_view,
                                                         target_data=refdata,
                                                         broadcast=False, subset_state=ss)
                    if transpose:
                        buf = buf.transpose()

                    vf = np.vectorize(int)
                    img = vf(buf)
                    rgb_color = to_rgb(color)

                    # We use alpha = 0 for the bottom of the colorscale since we don't want
                    # anything outside the subset to contribute
                    colorscale = [[0, 'rgba(0,0,0,0)'], [1, 'rgb{0}'.format(tuple(int(256 * v) for v in rgb_color))]]
                    image_info = dict(
                        z=img,
                        colorscale=colorscale,
                        hoverinfo='skip',
                        name=layer_state.layer.label,
                        opacity=layer_state.alpha * 0.5,
                        showscale=False,
                        showlegend=True
                    )
                    layers_to_add.append([layer.zorder, fig.add_heatmap, image_info])


            elif isinstance(layer_state, ScatterLayerState):
                x = layer_state.layer[viewer_state.x_att]
                y = layer_state.layer[viewer_state.y_att]

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
                    rgb_str = [r'{}'.format(rgb2hex(
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
                layers_to_add.append([layer.zorder, fig.add_scatter, scatter_info])

        # The background color is a weighted sum of the bottom (0) color
        # of the colorscales for each of the image layers
        alpha_sum = sum(x[0] for x in bg_colors)
        print(alpha_sum)
        bg_color = []
        print(bg_colors)
        if alpha_sum != 0:
            for i in range(3):
                s = sum((color[i] ** 2) * (w / alpha_sum) for w, color in bg_colors)
                bg_color.append(int(256 * sqrt(s)))
            bg_color.append(alpha_sum / len(bg_colors))
        else:
            v = 256 if using_colormaps else 0
            bg_color = [v, v, v, 1]
        print(bg_color)
        fig.update_layout(plot_bgcolor='rgba{0}'.format(tuple(bg_color)))

        # This block of code adds an all-white or background-colored heatmap as the bottom layer
        # to match what we see in glue
        axes = sorted([viewer_state.x_att.axis, viewer_state.y_att.axis])
        shape = [viewer_state.reference_data.shape[i] for i in axes]
        bg = np.ones(shape)
        color = 'rgb(256,256,256)' if using_colormaps else 'rgba{0}'.format(tuple(bg_color))
        bg_info = dict(z=bg,
                       colorscale=[[0, color], [1, color]],
                       hoverinfo='skip',
                       opacity=1,
                       showscale=False)

        layers_to_add.append([-1, fig.add_heatmap, bg_info])

        for _zorder, func, data in sorted(layers_to_add, key=lambda l: l[0]):
            func(**data)

        plot(fig, filename=filename, auto_open=False)
