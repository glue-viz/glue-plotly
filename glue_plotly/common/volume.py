from glue_plotly.utils import rgba_components
from numpy import array, linspace, meshgrid, nan_to_num, nanmin

from glue.core.state_objects import State
from glue.core.subset_group import GroupedSubset

from glue_plotly.common import color_info
from glue_plotly.common.base_3d import bbox_mask

import plotly.graph_objects as go


def positions(bounds):
    # The viewer bounds are in reverse order
    coord_arrays = [linspace(b[0], b[1], num=b[2]) for b in reversed(bounds)]
    return meshgrid(*coord_arrays)


def parent_layer(viewer_or_state, subset):
    data = subset.data
    for layer in viewer_or_state.layers:
        if layer.layer is data:
            return layer
    return None


# TODO: Can we write this function entirely in terms of the viewer and layer states?
# We probably can, if we don't on the data proxies
def values(viewer, layer, bounds, precomputed=None):
    subset_layer = isinstance(layer.layer, GroupedSubset)
    parent = layer.layer.data if subset_layer else layer.layer
    parent_label = parent.label
    parent_artist = parent_layer(viewer, layer.layer) if subset_layer else layer
    if precomputed is not None and parent_label in precomputed:
        data = precomputed[parent_label]
    elif parent_artist is not None:
        data = parent_artist._data_proxy.compute_fixed_resolution_buffer(bounds)
    else:
        data = parent.compute_fixed_resolution_buffer(
                   target_data=viewer.state.reference_data,
                   bounds=bounds,
                   target_cid=layer.state.attribute)

    if subset_layer:
        subcube = layer._data_proxy.compute_fixed_resolution_buffer(bounds)
        values = subcube * data
    else:
        values = data

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


def isomin_for_layer(viewer_or_state, layer):
    if isinstance(layer.layer, GroupedSubset):
        parent = parent_layer(viewer_or_state, layer.layer)
        if parent is not None:
            parent_state = parent if isinstance(parent, State) else parent.state
            return parent_state.vmin

    state = layer if isinstance(layer, State) else layer 
    return state.vmin


def isomax_for_layer(viewer_or_state, layer):
    if isinstance(layer.layer, GroupedSubset):
        parent = parent_layer(viewer_or_state, layer.layer)
        if parent is not None:
            parent_state = parent if isinstance(parent, State) else parent.state
            return parent_state.vmax

    state = layer if isinstance(layer, State) else layer 
    return state.vmax


def traces_for_layer(viewer, layer, bounds, isosurface_count=5):

    xyz = positions(bounds)
    state = layer.state
    mask = bbox_mask(viewer.state, *xyz)
    clipped_xyz = [c[mask] for c in xyz]
    clipped_values = values(viewer, layer, bounds)[mask]
    return [go.Volume(
       x=clipped_xyz[0],
       y=clipped_xyz[1],
       z=clipped_xyz[2],
       value=clipped_values,
       colorscale=colorscale(state),
       opacityscale=opacity_scale(state),
       isomin=isomin_for_layer(viewer.state, state),
       isomax=isomax_for_layer(viewer.state, state),
       opacity=state.alpha,
       surface_count=isosurface_count,
       showscale=False
    )]
