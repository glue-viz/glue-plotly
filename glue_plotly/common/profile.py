from glue.core import BaseData
from plotly.graph_objs import Scatter

from glue_plotly.common import fixed_color
from glue_plotly.common.histogram import axis_from_mpl, layout_config, layout_config_from_mpl  # noqa


def traces_for_layer(viewer_state, layer_state, add_data_label=True):
    x, y = layer_state.profile
    if viewer_state.normalize:
        y = layer_state.normalize_values(y)
    line = dict(width=2 * layer_state.linewidth,
                shape='hvh' if layer_state.as_steps else 'linear',
                color=fixed_color(layer_state))

    name = layer_state.layer.label
    if add_data_label and not isinstance(layer_state.layer, BaseData):
        name += " ({0})".format(layer_state.layer.data.label)

    profile_info = dict(hoverinfo='skip', line=line,
                        opacity=layer_state.alpha, name=name,
                        x=x, y=y)

    return [Scatter(**profile_info)]
