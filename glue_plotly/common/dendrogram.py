from glue.core import BaseData
from glue_plotly.common import base_layout_config, base_rectilinear_axis, fixed_color

from plotly.graph_objs import Scatter


def x_axis(viewer_state):
    return dict(
        showticklabels=False,
        showline=False,
        showgrid=False,
        range=[viewer_state.x_min, viewer_state.x_max]
    )


def layout_config_from_mpl(viewer):
    config = base_layout_config(viewer)
    xaxis = x_axis(viewer.state)
    yaxis = base_rectilinear_axis(viewer.state, 'y')
    config.update(xaxis=xaxis, yaxis=yaxis)
    return config


def trace_for_layer(layer_state, data, add_data_label=True):
    name = layer_state.layer.label
    if add_data_label and not isinstance(layer_state.layer, BaseData):
        name += " ({0})".format(layer_state.layer.data.label)
    return Scatter(
        mode='lines',
        x=data[:, 0],
        y=data[:, 1],
        name=name,
        hoverinfo='skip',
        line=dict(width=1.5 * layer_state.linewidth,
                  color=fixed_color(layer_state)),
        opacity=layer_state.alpha
    )
