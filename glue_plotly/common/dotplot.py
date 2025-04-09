from uuid import uuid4

from numpy import isfinite
from plotly.graph_objs import Scatter

from glue.core import BaseData
from glue_plotly.common import color_info, dimensions
from glue_plotly.viewers.common import PlotlyBaseView


def dot_size(viewer, layer_state):
    edges = layer_state.histogram[0]
    viewer_state = viewer.state
    diam_world = min([edges[i + 1] - edges[i] for i in range(len(edges) - 1)])
    width, height = dimensions(viewer)
    if isinstance(viewer, PlotlyBaseView):
        margins = viewer.figure.layout.margin
        if margins:
            height -= (margins.b + margins.t)
            width -= (margins.l + margins.r)
    diam = diam_world * width / abs(viewer_state.x_max - viewer_state.x_min)
    if viewer_state.y_min is not None \
            and viewer_state.y_max is not None \
            and viewer_state.y_min != viewer_state.y_max:
        diam_pixel_v = height / abs(viewer_state.y_max - viewer_state.y_min)
        diam = min(diam_pixel_v, diam)
    if not isfinite(diam):
        diam = 1
    return diam * 0.95


def dot_positions(layer_state):
    x = []
    y = []
    edges, counts = layer_state.histogram
    counts = counts.astype(int)
    for i in range(len(edges) - 1):
        x_i = (edges[i] + edges[i + 1]) / 2
        y_i = range(1, counts[i] + 1)
        x.extend([x_i] * counts[i])
        y.extend(y_i)

    return x, y


def dots_for_layer(viewer, layer_state, add_data_label=True):
    legend_group = uuid4().hex
    dots_id = uuid4().hex

    x, y = dot_positions(layer_state)

    radius = dot_size(viewer, layer_state)
    marker = dict(color=color_info(layer_state, mask=None), size=radius)

    name = layer_state.layer.label
    if add_data_label and not isinstance(layer_state.layer, BaseData):
        name += f" ({layer_state.layer.data.label})"

    return Scatter(
        x=x,
        y=y,
        mode="markers",
        marker=marker,
        name=name,
        legendgroup=legend_group,
        meta=dots_id,
    )


def traces_for_layer(viewer, layer_state, add_data_label=True):
    return [dots_for_layer(viewer, layer_state, add_data_label=add_data_label)]
