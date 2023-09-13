from uuid import uuid4

from glue.core import BaseData
from plotly.graph_objs import Bar

from glue_plotly.common import base_layout_config, fixed_color, base_rectilinear_axis
from glue_plotly.utils import mpl_ticks_values


def axis_from_mpl(viewer, ax, glue_ticks=True):
    a = base_rectilinear_axis(viewer.state, ax)
    if glue_ticks:
        vals, text = mpl_ticks_values(viewer.axes, ax)
        if vals and text:
            a.update(tickmode='array', tickvals=vals, ticktext=text)
    return a


def layout_config(viewer, **kwargs):
    kwargs.setdefault("barmode", "overlay")
    kwargs.setdefault("bargap", 0)
    config = base_layout_config(viewer, **kwargs)
    x_axis = base_rectilinear_axis(viewer.state, 'x')
    y_axis = base_rectilinear_axis(viewer.state, 'y')
    config.update(xaxis=x_axis, yaxis=y_axis)
    return config


def layout_config_from_mpl(viewer, **kwargs):
    kwargs.setdefault("barmode", "overlay")
    kwargs.setdefault("bargap", 0)
    config = base_layout_config(viewer, **kwargs)
    x_axis = axis_from_mpl(viewer, 'x')
    y_axis = axis_from_mpl(viewer, 'y')
    config.update(xaxis=x_axis, yaxis=y_axis)
    return config


def traces_for_layer(viewer_state, layer_state, add_data_label=True):
    traces = []
    legend_group = uuid4().hex
    bars_id = uuid4().hex

    # The x values should be at the midpoints between successive pairs of edge values
    edges, y = layer_state.histogram
    x = [0.5 * (edges[i] + edges[i + 1]) for i in range(len(edges) - 1)]

    # set the opacity and remove bar borders
    # set all bars to be the same color
    marker = dict(opacity=layer_state.alpha,
                  line=dict(width=0),
                  color=fixed_color(layer_state))

    name = layer_state.layer.label
    if add_data_label and not isinstance(layer_state.layer, BaseData):
        name += " ({0})".format(layer_state.layer.data.label)

    hist_info = dict(hoverinfo="skip", marker=marker, name=name)
    if viewer_state.x_log:
        for i in range(len(x)):
            hist_info.update(
                legendgroup=legend_group,
                showlegend=i == 0,
                x=[x[i]],
                y=[y[i]],
                width=edges[i + 1] - edges[i],
                meta=bars_id
            )
            traces.append(Bar(**hist_info))
    else:
        hist_info.update(
            x=x,
            y=y,
            meta=bars_id
        )
        traces.append(Bar(**hist_info))

    return traces
