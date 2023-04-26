from matplotlib.colors import Normalize
import numpy as np

from glue.config import settings
from glue.core import BaseData

DEFAULT_FONT = 'Arial, sans-serif'


def dimensions(viewer):
    return viewer.figure.get_size_inches() * viewer.figure.dpi


def layers_to_export(viewer):
    return list(filter(lambda artist: artist.enabled and artist.visible, viewer.layers))


# Count the number of unique Data objects (either directly or as parents of subsets)
# used in the set of layers
def data_count(layers):
    data = set(layer.layer if isinstance(layer.layer, BaseData) else layer.layer.data for layer in layers)
    return len(data)


def base_layout_config(viewer, **kwargs):
    # set the aspect ratio of the axes, the tick label size, the axis label
    # sizes, and the axes limits
    width, height = dimensions(viewer)

    config = dict(
        margin=dict(r=50, l=50, b=50, t=50),  # noqa
        width=1200,
        height=1200 * height / width,  # scale axis correctly
        paper_bgcolor=settings.BACKGROUND_COLOR,
        plot_bgcolor=settings.BACKGROUND_COLOR
    )
    config.update(kwargs)
    return config


def rectilinear_axis(viewer, axis):
    title = getattr(viewer.axes, f'get_{axis}label')()
    ax = getattr(viewer.axes, f'{axis}axis')
    range = [getattr(viewer.state, f'{axis}_min'), getattr(viewer.state, f'{axis}_max')]
    log = getattr(viewer.state, f'{axis}_log')
    if log:
        range = [np.log10(b) for b in range]
    axis_dict = dict(
        title=title,
        titlefont=dict(
            family=DEFAULT_FONT,
            size=2 * ax.get_label().get_size(),
            color=settings.FOREGROUND_COLOR
        ),
        showspikes=False,
        linecolor=settings.FOREGROUND_COLOR,
        tickcolor=settings.FOREGROUND_COLOR,
        zeroline=False,
        mirror=True,
        ticks='outside',
        showline=True,
        showgrid=False,
        showticklabels=True,
        tickfont=dict(
            family=DEFAULT_FONT,
            size=1.5 * ax.get_ticklabels()[
                0].get_fontsize(),
            color=settings.FOREGROUND_COLOR),
        range=range,
        type='log' if log else 'linear',
        rangemode='normal',
    )
    if log:
        axis_dict.update(dtick=1, minor_ticks='outside')
    return axis_dict


def sanitize(*arrays):
    mask = np.ones(arrays[0].shape, dtype=bool)
    for a in arrays:
        try:
            mask &= (~np.isnan(a))
        except TypeError:  # non-numeric dtype
            pass

    return mask, tuple(a[mask].ravel() for a in arrays)


def fixed_color(layer):
    layer_color = layer.state.color
    if layer_color == '0.35':
        layer_color = 'gray'
    return layer_color


def rgb_colors(layer, mask, cmap_att):
    layer_state = layer.state
    if layer_state.cmap_vmin > layer_state.cmap_vmax:
        cmap = layer_state.cmap.reversed()
        norm = Normalize(
            vmin=layer_state.cmap_vmax, vmax=layer_state.cmap_vmin)
    else:
        cmap = layer_state.cmap
        norm = Normalize(
            vmin=layer_state.cmap_vmin, vmax=layer_state.cmap_vmax)

    color_values = layer_state.layer[getattr(layer_state, cmap_att)].copy()
    if mask is not None:
        color_values = color_values[mask]
    rgba_list = np.array([
        cmap(norm(point)) for point in color_values])
    rgba_list = [[int(256 * t) for t in rgba] for rgba in rgba_list]
    rgba_strs = [f'rgba({r},{g},{b},{a})' for r, g, b, a in rgba_list]
    return rgba_strs


def color_info(layer, mask=None,
               mode_att="cmap_mode",
               cmap_att="cmap_att"):
    if getattr(layer.state, mode_att) == "Fixed":
        return fixed_color(layer)
    else:
        return rgb_colors(layer, mask, cmap_att)
