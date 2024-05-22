from glue_plotly.utils import rgba_components
from numpy import array, linspace, meshgrid, nan_to_num, nanmin

from glue.core.subset_group import GroupedSubset

from glue_plotly.common import color_info
from glue_plotly.common.base_3d import bbox_mask

import plotly.graph_objects as go


def positions(bounds):
    # The viewer bounds are in reverse order
    coord_arrays = [linspace(b[0], b[1], num=b[2]) for b in reversed(bounds)]
    return meshgrid(*coord_arrays)


def values(data_proxy, bounds):
    values = data_proxy.compute_fixed_resolution_buffer(bounds)
    # This accounts for two transformations: the fact that the viewer bounds are in reverse order,
    # plus a need to change R -> L handedness for Plotly
    values = values.transpose(1, 2, 0)
    min_value = nanmin(values)
    replacement = min_value - 1
    replaced = nan_to_num(values, replacement)
    return replaced 


def colorscale(layer_state, size=10):
    color = color_info(layer_state)
    r, g, b, a = rgba_components(color)
    fractions = [(i / size) ** 0.25 for i in range(size + 1)]
    return [f"rgba({f*r},{f*g},{f*b},{f*a})" for f in fractions]


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


def traces_for_layer(viewer_state, layer, bounds, isosurface_count=5):

    xyz = positions(bounds)
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
       surface_count=isosurface_count
    )]
