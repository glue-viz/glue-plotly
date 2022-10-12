from __future__ import absolute_import, division, print_function

from collections import defaultdict

from astropy.visualization import (ManualInterval, ContrastBiasStretch)
import numpy as np
from matplotlib.colors import rgb2hex, to_rgb, Normalize

from qtpy import compat
from glue.config import viewer_tool, settings

from glue.core import DataCollection, Data
from glue.core.exceptions import IncompatibleAttribute
from glue.utils import ensure_numerical
from glue.viewers.image.pixel_selection_subset_state import PixelSubsetState
from glue.viewers.image.composite_array import STRETCHES
from glue.viewers.image.state import ImageLayerState, ImageSubsetLayerState
from glue.viewers.scatter.state import ScatterLayerState

from .. import save_hover

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

import plotly.graph_objects as go
from plotly.offline import plot
from plotly.subplots import make_subplots

DEFAULT_FONT = 'Arial, sans-serif'


def slice_to_bound(slc, size):
    min, max, step = slc.indices(size)
    n = (max - min - 1) // step
    max = min + step * n
    return min, max, n + 1


def cleaned_labels(labels):
    cleaned = [label.replace('\\mathregular', '\\mathrm') for label in labels]
    for j in range(len(cleaned)):
        label = cleaned[j]
        if '$' in label:
            cleaned[j] = '${0}$'.format(label.replace('$', ''))
    return cleaned


@viewer_tool
class PlotlyImage2DExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotlyimage2d'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        # grab hover info
        layers = sorted([layer for layer in self.viewer.layers if layer.state.visible and layer.enabled],
                        key=lambda l: l.zorder)
        scatter_layers, image_layers, image_subset_layers = [], [], []
        for layer in layers:
            if isinstance(layer.state, ImageLayerState):
                image_layers.append(layer)
            elif isinstance(layer.state, ImageSubsetLayerState):
                image_subset_layers.append(layer)
            elif isinstance(layer.state, ScatterLayerState):
                scatter_layers.append(layer)

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
        axes = self.viewer.axes

        # set the aspect ratio of the axes, the tick label size, the axis label
        # sizes, and the axes limits
        using_colormaps = viewer_state.color_mode == 'Colormaps'
        bg_color = [256, 256, 256, 1] if using_colormaps else [0, 0, 0, 1]
        layout_config = dict(
            margin=dict(r=50, l=50, b=50, t=50),  # noqa
            width=1200,
            height=1200 * height / width,  # scale axis correctly
            paper_bgcolor=settings.BACKGROUND_COLOR,
            plot_bgcolor='rgba{0}'.format(tuple(bg_color)),
            showlegend=True
        )

        axis_data = {}
        secondary_x = False
        secondary_y = False
        for helper in axes.coords:
            ticks = helper.ticks
            ticklabels = helper.ticklabels
            for axis in ticklabels.get_visible_axes():
                xy = 'x' if axis in ['t', 'b'] else 'y'
                xy_idx = 0 if xy == 'x' else 1
                locations = sorted([loc[0][xy_idx] for loc in ticks.ticks_locs[axis]])
                labels = ticklabels.text[axis]
                if xy == 'y':
                    labels = list(reversed(labels))
                labels = cleaned_labels(labels)
                if xy == 'x':
                    axis_range = [xmin, xmax]
                else:
                    axis_range = [ymin, ymax]
                axis_info = dict(
                    showspikes=False,
                    linecolor=settings.FOREGROUND_COLOR,
                    tickcolor=settings.FOREGROUND_COLOR,
                    ticks='outside',
                    zeroline=False,
                    showline=False,
                    showgrid=False,
                    range=axis_range,
                    showticklabels=True,
                    tickmode='array',
                    tickvals=locations,
                    ticktext=labels,
                    tickfont=dict(
                        family=DEFAULT_FONT,
                        size=1.5 * self.viewer.axes.xaxis.get_ticklabels()[
                            0].get_fontsize(),
                        color=settings.FOREGROUND_COLOR)
                )

                if axis == 'b':
                    axis_info.update(
                        title=self.viewer.axes.get_xlabel(),
                        titlefont=dict(
                            family=DEFAULT_FONT,
                            size=2 * self.viewer.axes.xaxis.get_label().get_size(),
                            color=settings.FOREGROUND_COLOR
                        ),
                    )
                    axis_data["xaxis"] = axis_info
                elif axis == 'l':
                    axis_info.update(
                        title=self.viewer.axes.get_ylabel(),
                        titlefont=dict(
                            family=DEFAULT_FONT,
                            size=2 * self.viewer.axes.yaxis.get_label().get_size(),
                            color=settings.FOREGROUND_COLOR
                        ),
                    )
                    axis_data["yaxis"] = axis_info
                elif axis == 't':
                    axis_info.update(overlaying='x', side='top')
                    axis_data["xaxis2"] = axis_info
                    secondary_x = True
                elif axis == 'r':
                    axis_info.update(overlaying='y', side='right')
                    axis_data["yaxis2"] = axis_info
                    secondary_y = True
                else:
                    continue

        layout_config.update(**axis_data)

        if secondary_x or secondary_y:
            fig = make_subplots(specs=[[{"secondary_y": True}]], horizontal_spacing=0, vertical_spacing=0)
            fig.update_layout(**layout_config)
        else:
            layout = go.Layout(**layout_config)
            fig = go.Figure(layout=layout)

        has_nonpixel_subset = any(not isinstance(layer.layer.subset_state, PixelSubsetState)
                                  for layer in image_subset_layers)
        if has_nonpixel_subset:
            full_view, agg_func, transpose = viewer_state.numpy_slice_aggregation_transpose
            full_view[viewer_state.x_att.axis] = slice(None)
            full_view[viewer_state.y_att.axis] = slice(None)
            for i in range(viewer_state.reference_data.ndim):
                if isinstance(full_view[i], slice):
                    full_view[i] = slice_to_bound(full_view[i], viewer_state.reference_data.shape[i])

        # This block of code adds an all-white heatmap as the bottom layer when using colormaps
        # to match what we see in glue
        if using_colormaps:
            xy_axes = sorted([viewer_state.x_att.axis, viewer_state.y_att.axis])
            shape = [viewer_state.reference_data.shape[i] for i in xy_axes]
            bg = np.ones(shape)
            legend_groups = defaultdict(int)
            bottom_color = (256, 256, 256)
            bottom_colorstring = 'rgb{0}'.format(bottom_color)
            bottom_info = dict(z=bg,
                               colorscale=[[0, bottom_colorstring], [1, bottom_colorstring]],
                               hoverinfo='skip',
                               opacity=1,
                               showscale=False)

            layers_to_add = [[fig.add_heatmap, bottom_info]]

            for i, layer in enumerate(image_layers):

                layer_state = layer.state

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

                if layer_state.v_min > layer_state.v_max:
                    cmap = layer_state.cmap.reversed()
                    bounds = [layer_state.v_max, layer_state.v_min]
                else:
                    cmap = layer_state.cmap
                    bounds = [layer_state.v_min, layer_state.v_max]
                mapped_bounds = STRETCHES[layer_state.stretch]()(contrast_bias(interval(bounds)))
                unmapped_space = np.linspace(0, 1, 60)
                mapped_space = np.linspace(mapped_bounds[0], mapped_bounds[1], 60)
                color_space = [cmap(b)[:3] for b in mapped_space]
                color_values = [tuple(256 * v for v in p) for p in color_space]
                colorscale = [[0, 'rgb{0}'.format(color_values[0])]] + \
                             [[u, 'rgb{0}'.format(c)] for u, c in zip(unmapped_space, color_values)] + \
                             [[1, 'rgb{0}'.format(color_values[-1])]]

                image_info = dict(
                    z=img,
                    colorscale=colorscale,
                    hoverinfo='skip',
                    xaxis='x',
                    yaxis='y',
                    zmin=mapped_bounds[0],
                    zmax=mapped_bounds[1],
                    name=layer_state.layer.label,
                    showscale=False,
                    showlegend=True,
                    opacity=layer_state.alpha
                )
                layers_to_add.append([fig.add_heatmap, image_info])

        else:
            img = self.viewer.axes._composite()
            img[:, :, :3] *= 256
            image_info = dict(
                z=img,
                opacity=1,
                hoverinfo='skip'
            )
            bg_color = img[0][0]
            fig.update_layout(plot_bgcolor='rgba{0}'.format(tuple(bg_color)))
            layers_to_add = [[fig.add_image, image_info]]

        for layer in image_subset_layers:
            layer_state = layer.state
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

                    x_line_data = {**line_data, 'x': [x, x], 'y': [ymin, ymax], 'showlegend': True}
                    y_line_data = {**line_data, 'x': [xmin, xmax], 'y': [y, y], 'showlegend': False}
                    layers_to_add.append([fig.add_scatter, x_line_data])
                    layers_to_add.append([fig.add_scatter, y_line_data])
                except IncompatibleAttribute:
                    pass
            else:
                color = 'gray' if layer_state.color == '0.35' else layer_state.color
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
                colorscale = [[0, 'rgba(0,0,0,0)'], [1, 'rgb{0}'.format(tuple(256 * v for v in rgb_color))]]
                image_info = dict(
                    z=img,
                    colorscale=colorscale,
                    hoverinfo='skip',
                    xaxis='x',
                    yaxis='y',
                    name=layer_state.layer.label,
                    opacity=layer_state.alpha * 0.5,
                    showscale=False,
                    showlegend=True
                )
                layers_to_add.append([fig.add_heatmap, image_info])

        for layer in scatter_layers:
            layer_state = layer.state
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
                xaxis='x',
                yaxis='y',
                hoverinfo=hoverinfo,
                hovertext=hovertext,
                name=layer_state.layer.label
            )
            scatter_info.update(x=x, y=y)
            layers_to_add.append([fig.add_scatter, scatter_info])

        # This is a hack to force plotly to show the secondary axes, if there are any
        # We just put in a transparent heatmap assigned to whatever secondary axes exist
        if secondary_x or secondary_y:
            secondary_info = dict(z=bg,
                                  colorscale=[[0, 'rgb(0,0,0)'], [1, 'rgb(0,0,0)']],
                                  hoverinfo='skip',
                                  opacity=0,
                                  showscale=False,
                                  xaxis='x2' if secondary_x else 'x',
                                  yaxis='y2' if secondary_y else 'y')
            layers_to_add.append([fig.add_heatmap, secondary_info])

        for func, data in layers_to_add:
            func(**data)

        plot(fig, include_mathjax='cdn', filename=filename, auto_open=False)
