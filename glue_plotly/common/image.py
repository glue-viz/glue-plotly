from uuid import uuid4
from matplotlib.colors import to_rgb
import numpy as np

from glue.viewers.image.state import ImageLayerState, ImageSubsetLayerState
from glue.viewers.scatter.state import IncompatibleAttribute, ScatterLayerState

from plotly.graph_objects import Heatmap, Scatter

from glue_plotly.common import base_layout_config, fixed_color, layers_to_export


def slice_to_bound(slc, size):
    min, max, step = slc.indices(size)
    n = (max - min - 1) // step
    max = min + step * n
    return min, max, n + 1


def background_color(viewer):
    using_colormaps = viewer.state.color_mode == 'Colormaps'
    bg_color = [256, 256, 256, 1] if using_colormaps else [0, 0, 0, 1]
    return bg_color


def layout_config(viewer):
    bg_color = background_color(viewer)
    return base_layout_config(viewer,
                              plot_bgcolor='rgba{0}'.format(tuple(bg_color)),
                              showlegend=True)


def layers_by_type(viewer):
    layers = sorted(layers_to_export(viewer), key=lambda lyr: lyr.zorder)
    scatter_layers, image_layers, image_subset_layers = [], [], []
    for layer in layers:
        if isinstance(layer.state, ImageLayerState):
            image_layers.append(layer)
        elif isinstance(layer.state, ImageSubsetLayerState):
            image_subset_layers.append(layer)
        elif isinstance(layer.state, ScatterLayerState):
            scatter_layers.append(layer)

    return dict(scatter=scatter_layers, image=image_layers, image_subset=image_subset_layers)

def full_view_transpose(viewer):
    state = viewer.state
    full_view, _agg_func, transpose = state.numpy_slice_aggregation_transpose
    full_view[state.x_att.axis] = slice(None)
    full_view[state.y_att.axis] = slice(None)
    for i in range(state.reference_data.ndim):
        if isinstance(full_view[i], slice):
            full_view[i] = slice_to_bound(full_view[i], state.reference_data.shape[i])
    
    return full_view, transpose


def traces_for_pixel_subset_layer(viewer, layer):
    state = layer.state
    subset_state = layer.layer.subset_state
    xmin, xmax = viewer.axes.get_xlim()
    ymin, ymax = viewer.axes.get_ylim()

    try:
        x, y = subset_state.get_xy(layer.layer.data, viewer.state.x_att.axis, viewer.state.y_att.axis)
        line_data = dict(
            mode="lines",
            marker=dict(
                color=state.color
            ),
            opacity = state.alpha * 0.5,
            name = state.layer.label,
            legendgroup=uuid4()
        )

        x_line_data = {**line_data, 'x': [x, x], 'y': [ymin, ymax], 'showlegend': True}
        y_line_data = {**line_data, 'x': [xmin, xmax], 'y': [y, y], 'showlegend': False}
        return [Scatter(**x_line_data), Scatter(**y_line_data)]
    except IncompatibleAttribute:
        return []


def traces_for_nonpixel_subset_layer(viewer, layer, full_view, transpose):
    layer_state = layer.state
    subset_state = layer.layer.subset_state
    ref_data = viewer.state.reference_data
    color = fixed_color(layer)
    buffer = ref_data \
            .compute_fixed_resolution_buffer(full_view,
                                             target_data=ref_data,
                                             broadcast=False,
                                             subset_state=subset_state)
    if transpose:
        buffer = buffer.transpose()

    vf = np.vectorize(int)
    img = vf(buffer)
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

    return [Heatmap(**image_info)]
