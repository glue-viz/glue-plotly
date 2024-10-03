from glue_plotly.utils import frb_for_layer, rgba_components
from numpy import linspace, meshgrid, nan_to_num, nanmin

from glue.core import BaseData
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


def values(viewer_state, layer_state, bounds, precomputed=None):
    subset_layer = isinstance(layer_state.layer, GroupedSubset)
    parent = layer_state.layer.data if subset_layer else layer_state.layer
    parent_label = parent.label
    if precomputed is not None and parent_label in precomputed:
        values = precomputed[parent_label]
    else:
        values = frb_for_layer(viewer_state, layer_state, bounds)

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


def traces_for_layer(viewer_state, layer_state, bounds,
                     isosurface_count=5, add_data_label=True):

    xyz = positions(bounds)
    mask = bbox_mask(viewer_state, *xyz)
    clipped_xyz = [c[mask] for c in xyz]
    clipped_values = values(viewer_state, layer_state, bounds)[mask]
    name = layer_state.layer.label
    if add_data_label and not isinstance(layer_state.layer, BaseData):
        name += " ({0})".format(layer_state.layer.data.label)

    return [go.Volume(
       name=name,
       hoverinfo="skip",
       hovertext=None,
       x=clipped_xyz[0],
       y=clipped_xyz[1],
       z=clipped_xyz[2],
       value=clipped_values,
       colorscale=colorscale(layer_state),
       opacityscale=opacity_scale(layer_state),
       isomin=isomin_for_layer(viewer_state, layer_state),
       isomax=isomax_for_layer(viewer_state, layer_state),
       opacity=layer_state.alpha,
       surface_count=isosurface_count,
       showscale=False
    )]
