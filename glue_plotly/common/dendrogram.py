from glue.core import BaseData
from glue_plotly.common import base_layout_config, base_rectilinear_axis, fixed_color

from plotly.graph_objs import Scatter


def x_axis(viewer):
    return dict(
        showticklabels=False,
        showline=False,
        showgrid=False,
        range=[viewer.state.x_min, viewer.state.x_max]
    )


def layout_config(viewer):
    config = base_layout_config(viewer)
    xaxis = x_axis(viewer)
    yaxis = base_rectilinear_axis(viewer, 'y')
    config.update(xaxis=xaxis, yaxis=yaxis)
    return config


def trace_for_layer(layer, data, add_data_label=True):
    name = layer.layer.label
    if add_data_label and not isinstance(layer.layer, BaseData):
        name += " ({0})".format(layer.layer.data.label)
    return Scatter(
        mode='lines',
        x=data[:, 0],
        y=data[:, 1],
        name=name,
        hoverinfo='skip',
        line=dict(width=layer.state.linewidth,
                  color=fixed_color(layer)),
        opacity=layer.state.alpha
    )
