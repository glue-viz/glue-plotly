from uuid import uuid4

from plotly.graph_objs import Scatter

from glue.core import BaseData

from .common import color_info

def traces_for_layer(viewer_state, layer_state, add_data_label=True):
    legend_group = uuid4().hex
    dots_id = uuid4().hex

    x = []
    y = []
    edges, counts = layer_state.histogram
    counts = counts.astype(int)
    for i in range(len(edges) - 2):
        x_i = (edges[i] + edges[i + 1]) / 2
        y_i = range(1, counts[i] + 1)
        x.extend([x_i] * counts[i])
        y.extend(y_i)

    marker = dict(color=color_info(layer_state, mask=None))

    name = layer_state.layer.label
    if add_data_label and not isinstance(layer_state.layer, BaseData):
        name += " ({0})".format(layer_state.layer.data.label)

    return [Scatter(
        x=x,
        y=y,
        mode="markers",
        marker=marker,
        name=name,
        legendgroup=legend_group,
        meta=dots_id,
    )]
