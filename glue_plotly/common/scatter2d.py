from uuid import uuid4

import numpy as np
import plotly.graph_objs as go
import plotly.figure_factory as ff

from glue.config import settings
from glue.core import BaseData
from glue.utils import ensure_numerical
from glue.viewers.scatter.layer_artist import ColoredLineCollection

from .common import DEFAULT_FONT, base_layout_config, \
    base_rectilinear_axis, color_info, dimensions, sanitize

LINESTYLES = {'solid': 'solid', 'dotted': 'dot', 'dashed': 'dash', 'dashdot': 'dashdot'}


def projection_type(viewer_state):
    proj = viewer_state.plot_mode
    return 'azimuthal equal area' if proj == 'lambert' else proj


def angular_axis(viewer_state):
    degrees = viewer_state.using_degrees
    angle_unit = 'degrees' if degrees else 'radians'
    theta_prefix = ''
    if viewer_state.x_axislabel:
        theta_prefix = '{0}='.format(viewer_state.x_axislabel)

    return dict(
        type='linear',
        thetaunit=angle_unit,
        showticklabels=True,
        showtickprefix='first',
        tickprefix=theta_prefix,
        tickfont=dict(
            family=DEFAULT_FONT,
            size=1.5 * viewer_state.x_ticklabel_size,
            color=settings.FOREGROUND_COLOR),
        linecolor=settings.FOREGROUND_COLOR,
        gridcolor=settings.FOREGROUND_COLOR
    )


def radial_axis(viewer, tickvals=None, ticklabels=None):
    axis = dict(
        type='linear',
        range=[viewer.state.y_min, viewer.state.y_max],
        showticklabels=True,
        tickmode='array',
        angle=22.5,
        tickangle=22.5,
        showline=False,
        tickfont=dict(
            family=DEFAULT_FONT,
            size=1.5 * viewer.state.y_ticklabel_size,
            color=settings.FOREGROUND_COLOR),
        linecolor=settings.FOREGROUND_COLOR,
        gridcolor=settings.FOREGROUND_COLOR
    )

    if tickvals is not None and ticklabels is not None:
        axis.update(tickvals=tickvals,
                    ticktext=['<i>{0}</i>'.format(t) for t in ticklabels])
        return axis


def mpl_radial_axis(viewer):
    tickvals = viewer.axes.yaxis.get_majorticklocs()
    ticklabels = [t.get_text() for t in viewer.axes.yaxis.get_majorticklabels()]
    return radial_axis(viewer, tickvals, ticklabels)


def rectilinear_layout_config(viewer, **kwargs):
    layout_config = base_layout_config(viewer, **kwargs)
    x_axis = base_rectilinear_axis(viewer.state, 'x')
    y_axis = base_rectilinear_axis(viewer.state, 'y')
    layout_config.update(xaxis=x_axis, yaxis=y_axis)
    return layout_config


def polar_layout_config(viewer, radial_axis_maker, **kwargs):
    layout_config = base_layout_config(viewer, **kwargs)
    theta_axis = angular_axis(viewer.state)
    r_axis = radial_axis_maker(viewer)
    polar = go.layout.Polar(angularaxis=theta_axis, radialaxis=r_axis,
                            bgcolor=settings.BACKGROUND_COLOR)
    layout_config.update(polar=polar)
    return layout_config


def polar_layout_config_from_mpl(viewer, **kwargs):
    return polar_layout_config(viewer, mpl_radial_axis, **kwargs)


def scatter_mode(layer_state):
    if layer_state.line_visible and layer_state.cmap_mode == 'Fixed':
        return 'lines+markers'
    else:
        return 'markers'


def rectilinear_lines(layer_state, marker, x, y, legend_group=None):
    traces = []

    line = dict(dash=LINESTYLES[layer_state.linestyle], width=layer_state.linewidth)

    if layer_state.cmap_mode == 'Linear':
        line_id = uuid4().hex
        # set mode to markers and plot the colored line over it
        rgba_strs = marker['color']
        lc = ColoredLineCollection(x, y)
        segments = lc.get_segments()
        # generate list of indices to parse colors over
        indices = np.repeat(range(len(x)), 2)
        indices = indices[1:len(x) * 2 - 1]
        for i in range(len(segments)):
            traces.append(go.Scatter(
                x=[segments[i][0][0], segments[i][1][0]],
                y=[segments[i][0][1], segments[i][1][1]],
                mode='lines',
                legendgroup=legend_group,
                line=dict(
                    dash=LINESTYLES[layer_state.linestyle],
                    width=layer_state.linewidth,
                    color=rgba_strs[indices[i]]),
                showlegend=False,
                visible=layer_state.line_visible,
                hoverinfo='skip',
                meta=line_id)
            )

    return line, traces


def rectilinear_error_bars(layer_state, marker, mask, x, y, axis, legend_group=None):
    err = {}
    traces = []
    err_att = getattr(layer_state, f'{axis}err_att')
    err['type'] = 'data'
    err['array'] = ensure_numerical(layer_state.layer[err_att][mask].ravel())
    err['visible'] = True

    # add points with error bars here if color mode is linear
    if layer_state.cmap_mode == 'Linear':
        error_bar_id = uuid4().hex
        for i, bar in enumerate(err['array']):
            scatter_info = dict(
                x=[x[i]],
                y=[y[i]],
                mode='markers',
                marker=dict(color=marker['color'][i]),
                showlegend=False,
                legendgroup=legend_group,
                hoverinfo='skip',
                hovertext=None,
                meta=error_bar_id
            )
            scatter_info[f'error_{axis}'] = dict(
                type='data', color=marker['color'][i],
                array=[bar], visible=True)
            traces.append(go.Scatter(**scatter_info))

    return err, traces


def _adjusted_vector_points(origin, scale, x, y, vx, vy):
    vx = scale * vx
    vy = scale * vy
    if origin == 'tail':
        return x, y
    elif origin == 'middle':
        return x - 0.5 * vx, y - 0.5 * vy
    else:  # tip
        return x - vx, y - vy


def rectilinear_2d_vectors(viewer, layer_state, marker, mask, x, y, legend_group=None):
    width, _ = dimensions(viewer)
    vx = layer_state.layer[layer_state.vx_att][mask]
    vy = layer_state.layer[layer_state.vy_att][mask]
    if layer_state.vector_mode == 'Polar':
        theta, r = vx, vy
        theta = np.radians(theta)
        vx = r * np.cos(theta)
        vy = r * np.sin(theta)

    vmax = np.nanmax(np.hypot(vx, vy))
    diag = np.hypot(viewer.state.x_max - viewer.state.x_min,
                    viewer.state.y_max - viewer.state.y_min)
    scale = 0.05 * (layer_state.vector_scaling) * (diag / vmax) * (width / viewer.width())
    xrange = abs(viewer.state.x_max - viewer.state.x_min)
    yrange = abs(viewer.state.y_max - viewer.state.y_min)
    minfrac = min(xrange / diag, yrange / diag)
    arrow_scale = 0.2
    angle = np.pi * minfrac / 3 if layer_state.vector_arrowhead else 0
    vector_info = dict(scale=scale,
                       angle=angle,
                       name='quiver',
                       arrow_scale=arrow_scale,
                       line=dict(width=5),
                       legendgroup=legend_group,
                       showlegend=False,
                       hoverinfo='skip',
                       meta=uuid4().hex)
    x_vec, y_vec = _adjusted_vector_points(layer_state.vector_origin, scale, x, y, vx, vy)
    if layer_state.cmap_mode == 'Fixed':
        fig = ff.create_quiver(x_vec, y_vec, vx, vy, **vector_info)
        fig.update_traces(marker=dict(color=marker['color']))
    else:
        # start with the first quiver to add the rest
        color = marker['color'] if layer_state.fill else marker['line']['color']
        fig = ff.create_quiver([x[0]], [y[0]], [vx[0]], [vy[0]],
                               **vector_info, line_color=color[0])
        for i in range(1, len(color)):
            fig1 = ff.create_quiver([x[i]], [y[i]], [vx[i]], [vy[i]],
                                    **vector_info,
                                    line_color=color[i])
            fig.add_traces(data=fig1.data)

    return list(fig.data)


def size_info(layer_state, mask=None):

    # set all points to be the same size, with some arbitrary scaling
    if layer_state.size_mode == 'Fixed':
        return layer_state.size_scaling * layer_state.size

    # scale size of points by set size scaling
    else:
        data = layer_state.layer[layer_state.size_att]
        if mask is not None:
            data = data[mask]
        s = ensure_numerical(data.ravel())
        s = ((s - layer_state.size_vmin) /
             (layer_state.size_vmax - layer_state.size_vmin))
        # The following ensures that the sizes are in the
        # range 3 to 30 before the final size scaling.
        np.clip(s, 0, 1, out=s)
        s *= 0.95
        s += 0.05
        s *= (45 * layer_state.size_scaling)
        s[np.isnan(s)] = 0
        return s


def base_marker(layer_state, mask=None):
    color = color_info(layer_state, mask)
    marker = dict(size=size_info(layer_state, mask),
                  color=color,
                  opacity=layer_state.alpha)

    if layer_state.fill:
        marker['line'] = dict(width=0)
    else:
        marker['color'] = 'rgba(0,0,0,0)'
        marker['line'] = dict(width=1, color=color)

    return marker


def trace_data_for_layer(viewer, layer_state, hover_data=None, add_data_label=True):
    traces = {}
    if hover_data is None:
        hover_data = []

    x = layer_state.layer[viewer.state.x_att].copy()
    y = layer_state.layer[viewer.state.y_att].copy()
    mask, (x, y) = sanitize(x, y)

    legend_group = uuid4().hex

    rectilinear = getattr(viewer.state, 'using_rectilinear', True)

    marker = base_marker(layer_state, mask)

    # add vectors
    if rectilinear and layer_state.vector_visible and layer_state.vector_scaling > 0.1:
        vec_traces = rectilinear_2d_vectors(viewer, layer_state, marker, mask, x, y, legend_group)
        traces['vector'] = vec_traces

    # add line properties
    mode = scatter_mode(layer_state)
    if layer_state.line_visible:
        line, line_traces = rectilinear_lines(layer_state, marker, x, y, legend_group)
        if line_traces:
            traces['line'] = line_traces
    else:
        line = {}

    if rectilinear:
        if layer_state.xerr_visible:
            xerr, xerr_traces = rectilinear_error_bars(layer_state, marker, mask, x, y, 'x', legend_group)
            if xerr_traces:
                traces['xerr'] = xerr_traces
        if layer_state.yerr_visible:
            yerr, yerr_traces = rectilinear_error_bars(layer_state, marker, mask, x, y, 'y', legend_group)
            if yerr_traces:
                traces['yerr'] = yerr_traces

    if np.sum(hover_data) == 0:
        hoverinfo = 'skip'
        hovertext = None
    else:
        hoverinfo = 'text'
        hovertext = ["" for _ in range((mask.shape[0]))]
        for i in range(len(layer_state.layer.components)):
            if hover_data[i]:
                label = layer_state.layer.components[i].label
                hover_values = layer_state.layer[label][mask]
                for k in range(len(hover_values)):
                    hovertext[k] = (hovertext[k] + "{}: {} <br>"
                                    .format(label, hover_values[k]))

    name = layer_state.layer.label
    if add_data_label and not isinstance(layer_state.layer, BaseData):
        name += " ({0})".format(layer_state.layer.data.label)

    # The <extra></extra> removes 'trace <#>' from tooltip
    scatter_info = dict(
        mode=mode,
        marker=marker,
        line=line,
        hoverinfo=hoverinfo,
        hovertext=hovertext,
        name=name,
        legendgroup=legend_group
    )

    polar = getattr(viewer.state, 'using_polar', False)
    degrees = viewer.state.using_degrees
    proj = projection_type(viewer.state)
    if polar:
        scatter_info.update(theta=x, r=y, thetaunit='degrees' if degrees else 'radians')
        traces['scatter'] = [go.Scatterpolar(**scatter_info)]
    elif rectilinear:
        scatter_info.update(x=x, y=y)
        if layer_state.cmap_mode == 'Fixed':
            # add error bars here if the color mode was fixed
            if layer_state.xerr_visible:
                scatter_info.update(error_x=xerr)
            if layer_state.yerr_visible:
                scatter_info.update(error_y=yerr)
        traces['scatter'] = [go.Scatter(**scatter_info)]
    else:
        if not degrees:
            x = np.rad2deg(x)
            y = np.rad2deg(y)
        traces['scatter'] = [go.Scattergeo(lon=x, lat=y, projection_type=proj,
                                           showland=False, showcoastlines=False, showlakes=False,
                                           lataxis_showgrid=False, lonaxis_showgrid=False,
                                           bgcolor=settings.BACKGROUND_COLOR,
                                           framecolor=settings.FOREGROUND_COLOR)]

    return traces


def traces_for_layer(*args, **kwargs):
    trace_data = trace_data_for_layer(*args, **kwargs)
    return [trace for traces in trace_data.values() for trace in traces]
