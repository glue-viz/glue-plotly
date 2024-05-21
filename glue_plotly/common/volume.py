from numpy import array, linspace, meshgrid, nan_to_num, nanmin

from glue.core.subset_group import GroupedSubset

from glue_plotly.common import color_info
from glue_plotly.common.base_3d import bbox_mask

import plotly.graph_objects as go


def positions(bounds):
    coord_arrays = [linspace(b[0], b[1], num=b[2]) for b in reversed(bounds)]
    return meshgrid(*coord_arrays)


def values(data_proxy, bounds):
    values = data_proxy.compute_fixed_resolution_buffer(bounds)
    min_value = nanmin(values)
    replacement = min_value - 1
    replaced = nan_to_num(values, replacement)
    return replaced 


def colorscale(layer_state):
    color = color_info(layer_state)
    return [(0, "#000000"), (1, color)]


def opacity_scale(layer_state):
    return [[0, 0], [1, 1]]


def isomin_for_layer(viewer_state, layer_state):
    if isinstance(layer_state.layer, GroupedSubset):
        for viewer_layer in viewer_state.layers:
            if viewer_layer.layer is layer_state.layer.data:
                return viewer_layer.vmin

    return layer_state.vmin


def isomax_for_layer(viewer_state, layer_state):
    if isinstance(layer_state.layer, GroupedSubset):
        for viewer_layer in viewer_state.layers:
            if viewer_layer.layer is layer_state.layer.data:
                return viewer_layer.vmax

    return layer_state.vmax


def traces_for_layer(viewer_state, layer, bounds):

    xyz = positions(bounds)
    print([c.shape for c in xyz])
    state = layer.state
    mask = bbox_mask(viewer_state, *xyz)
    clipped_xyz = [c[mask] for c in xyz]
    clipped_values = values(layer._data_proxy, bounds)[mask]
    return [go.Volume(
       x=clipped_xyz[0],
       y=clipped_xyz[1],
       z=clipped_xyz[2],
       value=clipped_values,
       colorscale=colorscale(state),
       opacityscale=opacity_scale(state),
       isomin=isomin_for_layer(viewer_state, state),
       isomax=isomax_for_layer(viewer_state, state),
       opacity=state.alpha,
       surface_count=5
    )]


