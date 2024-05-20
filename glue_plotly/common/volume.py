from glue_plotly.common import color_info
from glue_plotly.common.base_3d import bbox_mask

import plotly.graph_objects as go


def positions(bounds):
    return [
        [(b[1] - b[0]) * (i + 0.5) / b[2] for i in range(b[2])] for b in bounds
    ]


def values(data_proxy, bounds):
    return data_proxy.compute_fixed_resolution_buffer(bounds)


def colorscale(layer_state):
    color = color_info(layer_state)
    return [(0, color), (1, color)]


def traces_for_layer(layer, bounds):

    xyz = positions(bounds)
    state = layer.state
    mask = bbox_mask(state, *xyz)
    clipped_xyz = [c[mask] for c in xyz]
    clipped_values = values(layer._data_proxy, bounds)[mask]
    return [go.Volume(
       x=clipped_xyz[0],
       y=clipped_xyz[1],
       z=clipped_xyz[2],
       value=clipped_values,
       isomin=0,
       isomax=1,
       opacity=state.alpha,
       surface_count=15
    )]


