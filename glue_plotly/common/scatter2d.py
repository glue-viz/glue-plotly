import matplotlib.colors as colors
from matplotlib.colors import Normalize
import numpy as np
import plotly.graph_objs as go

from glue.config import settings
from glue.utils import ensure_numerical
from glue.viewers.scatter.layer_artist import plot_colored_line

from glue_plotly.common import DEFAULT_FONT, base_layout_config, cartesian_axis


def angular_axis(viewer):
    degrees = viewer.state.using_degrees
    angle_unit = 'degrees' if degrees else 'radians'
    theta_prefix = ''
    if viewer.state.x_axislabel:
        theta_prefix = '{0}='.format(viewer.state.x_axislabel)

    return dict(
        type='linear',
        thetaunit=angle_unit,
        showticklabels=True,
        showtickprefix='first',
        tickprefix=theta_prefix,
        tickfont=dict(
            family=DEFAULT_FONT,
            size=1.5 * viewer.axes.xaxis.get_ticklabels()[
                0].get_fontsize(),
            color=settings.FOREGROUND_COLOR),
        linecolor=settings.FOREGROUND_COLOR,
        gridcolor=settings.FOREGROUND_COLOR
    )


def radial_axis(viewer):
    return dict(
        type='linear',
        range=[viewer.state.y_min, viewer.state.y_max],
        showticklabels=True,
        tickmode='array',
        tickvals=viewer.axes.yaxis.get_majorticklocs(),
        ticktext=['<i>{0}</i>'.format(t.get_text()) for t in viewer.axes.yaxis.get_majorticklabels()],
        angle=22.5,
        tickangle=22.5,
        showline=False,
        tickfont=dict(
            family=DEFAULT_FONT,
            size=1.5 * viewer.axes.yaxis.get_ticklabels()[
                0].get_fontsize(),
            color=settings.FOREGROUND_COLOR),
        linecolor=settings.FOREGROUND_COLOR,
        gridcolor=settings.FOREGROUND_COLOR
    )


def cartesian_layout_config(viewer):
    layout_config = base_layout_config(viewer)
    x_axis = cartesian_axis(viewer, 'x')
    y_axis = cartesian_axis(viewer, 'y')
    layout_config.update(xaxis=x_axis, yaxis=y_axis)
    return layout_config


def polar_layout_config(viewer):
    layout_config = base_layout_config(viewer)
    theta_axis = angular_axis(viewer)
    r_axis = radial_axis(viewer)
    polar = go.layout.Polar(angularaxis=theta_axis, radialaxis=r_axis,
                            bgcolor=settings.BACKGROUND_COLOR)
    layout_config.update(polar=polar)
    return layout_config


def cartesian_error_bars(layer, marker, x, y, axis='x'):
    err = {}
    traces = []
    x_axis = axis == 'x'
    err_att = layer.state.xerr_att if x_axis else layer.state.yerr_att
    err['type'] = 'data'
    err['array'] = ensure_numerical(layer.state.layer[err_att].ravel())
    err['visible'] = True

    # add points with error bars here if color mode is linear
    if layer.state.cmap_mode == 'Linear':
        for i, bar in enumerate(err['array']):
            traces.append(go.Scatter(
                x=[x[i]],
                y=[y[i]],
                mode='markers',
                error_x=dict(
                    type='data', color=marker['color'][i],
                    array=[bar], visible=True),
                marker=dict(color=marker['color'][i]),
                showlegend=False)
            )

    return err, traces


def traces_for_layer(viewer, layer):
    traces = []

    layer_state = layer.state

    x = layer_state.layer[viewer.state.x_att].copy()
    y = layer_state.layer[viewer.state.y_att].copy()

    rectilinear = getattr(viewer.state, 'using_rectilinear', True)

    marker = {}

    layer_color = layer_state.color
    if layer_color == '0.35':
        layer_color = 'gray'

    # set all points to be the same color
    if layer_state.cmap_mode == 'Fixed':
        marker['color'] = layer_color

    # color by some attribute
    else:
        if layer_state.cmap_vmin > layer_state.cmap_vmax:
            cmap = layer_state.cmap.reversed()
            norm = Normalize(
                vmin=layer_state.cmap_vmax, vmax=layer_state.cmap_vmin)
        else:
            cmap = layer_state.cmap
            norm = Normalize(
                vmin=layer_state.cmap_vmin, vmax=layer_state.cmap_vmax)

        # most matplotlib colormaps aren't recognized by plotly, so we convert manually to a hex code
        rgba_list = [
            cmap(norm(point)) for point in layer_state.layer[layer_state.cmap_att].copy()]
        rgb_str = [r'{}'.format(colors.rgb2hex(
            (rgba[0], rgba[1], rgba[2]))) for rgba in rgba_list]
        marker['color'] = rgb_str

    # set all points to be the same size, with some arbitrary scaling
    if layer_state.size_mode == 'Fixed':
        marker['size'] = 2 * layer_state.size_scaling * layer_state.size

    # scale size of points by set size scaling
    else:
        s = ensure_numerical(layer_state.layer[layer_state.size_att].ravel())
        s = ((s - layer_state.size_vmin) /
             (layer_state.size_vmax - layer_state.size_vmin))
        # The following ensures that the sizes are in the
        # range 3 to 30 before the final size scaling.
        np.clip(s, 0, 1, out=s)
        s *= 0.95
        s += 0.05
        s *= (30 * layer_state.size_scaling)
        marker['size'] = s

    # set the opacity
    marker['opacity'] = layer_state.alpha

    # check whether to fill circles

    if not layer_state.fill:
        marker['color'] = 'rgba(0,0,0,0)'
        marker['line'] = dict(width=1,
                              color=layer_state.color)

    else:
        # remove default white border around points
        marker['line'] = dict(width=0)

    # add line properties

    line = {}

    if layer_state.line_visible:
        # convert linestyle names from glue values to plotly values
        ls_dict = {'solid': 'solid', 'dotted': 'dot', 'dashed': 'dash', 'dashdot': 'dashdot'}
        line['dash'] = ls_dict[layer_state.linestyle]
        line['width'] = layer_state.linewidth

        if layer_state.cmap_mode == 'Fixed':
            marker['color'] = layer_color
            mode = 'lines+markers'
        else:
            # set mode to markers and plot the colored line over it
            mode = 'markers'
            lc = plot_colored_line(viewer.axes, x, y, rgb_str)
            segments = lc.get_segments()
            # generate list of indices to parse colors over
            indices = np.repeat(range(len(x)), 2)
            indices = indices[1:len(x) * 2 - 1]
            for i in range(len(segments)):
                traces.append(go.Scatter(
                    x=[segments[i][0][0], segments[i][1][0]],
                    y=[segments[i][0][1], segments[i][1][1]],
                    mode='lines',
                    line=dict(
                        dash=ls_dict[layer_state.linestyle],
                        width=layer_state.linewidth,
                        color=rgb_str[indices[i]]),
                    showlegend=False,
                    hoverinfo='skip')
                )
    else:
        mode = 'markers'


    if rectilinear:
        if layer_state.xerr_visible:
            xerr, xerr_traces = cartesian_error_bars(layer, marker, x, y, 'x')
        yerr, yerr_traces = cartesian_error_bars(layer, marker, x, y, 'y')
