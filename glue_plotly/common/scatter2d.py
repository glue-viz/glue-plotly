import numpy as np
import plotly.graph_objs as go
import plotly.figure_factory as ff

from glue.config import settings
from glue.utils import ensure_numerical
from glue.viewers.scatter.layer_artist import plot_colored_line

from .common import DEFAULT_FONT, base_layout_config,\
    rectilinear_axis, color_info, dimensions, sanitize

LINESTYLES = {'solid': 'solid', 'dotted': 'dot', 'dashed': 'dash', 'dashdot': 'dashdot'}


def projection_type(proj):
    return 'azimuthal equal area' if proj == 'lambert' else proj


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


def rectilinear_layout_config(viewer):
    layout_config = base_layout_config(viewer)
    x_axis = rectilinear_axis(viewer, 'x')
    y_axis = rectilinear_axis(viewer, 'y')
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


def rectilinear_lines(viewer, layer, marker, x, y, ):
    layer_state = layer.state

    line = dict(
        dash=LINESTYLES[layer_state.linestyle],
        width=layer_state.linewidth
    )

    traces = []

    if layer_state.cmap_mode == 'Fixed':
        mode = 'lines+markers'
    else:
        # set mode to markers and plot the colored line over it
        mode = 'markers'
        rgb_strs = marker['color']
        lc = plot_colored_line(viewer.axes, x, y, rgb_strs)
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
                    dash=LINESTYLES[layer_state.linestyle],
                    width=layer_state.linewidth,
                    color=rgb_strs[indices[i]]),
                showlegend=False,
                hoverinfo='skip')
            )

    return line, mode, traces


def rectilinear_error_bars(layer, marker, mask, x, y, axis):
    err = {}
    traces = []
    err_att = getattr(layer.state, f'{axis}err_att')
    err['type'] = 'data'
    err['array'] = ensure_numerical(layer.state.layer[err_att][mask].ravel())
    err['visible'] = True

    # add points with error bars here if color mode is linear
    if layer.state.cmap_mode == 'Linear':
        for i, bar in enumerate(err['array']):
            scatter_info = dict(
                x=[x[i]],
                y=[y[i]],
                mode='markers',
                marker=dict(color=marker['color'][i]),
                showlegend=False,
                hoverinfo='skip',
                hovertext=None
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


def rectilinear_2d_vectors(viewer, layer, marker, mask, x, y):
    width, _ = dimensions(viewer)
    layer_state = layer.state
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
                       showlegend=False, hoverinfo='skip')
    x_vec, y_vec = _adjusted_vector_points(layer_state.vector_origin, scale, x, y, vx, vy)
    if layer_state.cmap_mode == 'Fixed':
        fig = ff.create_quiver(x_vec, y_vec, vx, vy, **vector_info)
        fig.update_traces(marker=dict(color=marker['color']))

    else:
        # start with the first quiver to add the rest
        fig = ff.create_quiver([x[0]], [y[0]], [vx[0]], [vy[0]],
                               **vector_info, line_color=marker['color'][0])
        for i in range(1, len(marker['color'])):
            fig1 = ff.create_quiver([x[i]], [y[i]], [vx[i]], [vy[i]],
                                    **vector_info,
                                    line_color=marker['color'][i])
            fig.add_traces(data=fig1.data)

    return list(fig.data)


def traces_for_layer(viewer, layer, hover_data=None):
    traces = []
    if hover_data is None:
        hover_data = []

    layer_state = layer.state

    x = layer_state.layer[viewer.state.x_att].copy()
    y = layer_state.layer[viewer.state.y_att].copy()
    mask, (x, y) = sanitize(x, y)

    rectilinear = getattr(viewer.state, 'using_rectilinear', True)

    marker = dict(color=color_info(layer, mask),
                  opacity=layer_state.alpha)

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

    # check whether to fill circles
    if not layer_state.fill:
        marker['color'] = 'rgba(0,0,0,0)'
        marker['line'] = dict(width=1,
                              color=layer_state.color)

    else:
        # remove default white border around points
        marker['line'] = dict(width=0)

    # add vectors
    if rectilinear and layer.state.vector_visible and layer.state.vector_scaling > 0.1:
        vec_traces = rectilinear_2d_vectors(viewer, layer, marker, mask, x, y)
        traces += vec_traces

    # add line properties
    mode = "markers"
    line = {}
    if layer_state.line_visible:
        line, mode, line_traces = rectilinear_lines(viewer, layer, marker, x, y)
        traces += line_traces

    if rectilinear:
        if layer_state.xerr_visible:
            xerr, xerr_traces = rectilinear_error_bars(layer, marker, mask, x, y, 'x')
            traces += xerr_traces
        if layer_state.yerr_visible:
            yerr, yerr_traces = rectilinear_error_bars(layer, marker, mask, x, y, 'y')
            traces += yerr_traces

    if np.sum(hover_data) == 0:
        hoverinfo = 'skip'
        hovertext = None
    else:
        hoverinfo = 'text'
        hovertext = ["" for _ in range((layer_state.layer.shape[0]))]
        for i in range(0, len(layer_state.layer.components)):
            if hover_data[i]:
                hover_values = layer_state.layer[layer_state.layer.components[i].label][mask]
                for k in range(0, len(hover_values)):
                    hovertext[k] = (hovertext[k] + "{}: {} <br>"
                                    .format(layer_state.layer.components[i].label,
                                            hover_values[k]))

    # The <extra></extra> removes 'trace <#>' from tooltip
    scatter_info = dict(
        mode=mode,
        marker=marker,
        line=line,
        hoverinfo=hoverinfo,
        hovertext=hovertext,
        name=layer_state.layer.label
    )

    polar = getattr(viewer.state, 'using_polar', False)
    degrees = viewer.state.using_degrees
    proj = projection_type(viewer.state.plot_mode)
    if polar:
        scatter_info.update(theta=x, r=y, thetaunit='degrees' if degrees else 'radians')
        traces.append(go.Scatterpolar(**scatter_info))
    elif rectilinear:
        scatter_info.update(x=x, y=y)
        if layer_state.cmap_mode == 'Fixed':
            # add error bars here if the color mode was fixed
            if layer_state.xerr_visible:
                scatter_info.update(error_x=xerr)
            if layer_state.yerr_visible:
                scatter_info.update(error_y=yerr)
        traces.append(go.Scatter(**scatter_info))
    else:
        if not degrees:
            x = np.rad2deg(x)
            y = np.rad2deg(y)
        traces.append(go.Scattergeo(lon=x, lat=y, projection_type=proj,
                                    showland=False, showcoastlines=False, showlakes=False,
                                    lataxis_showgrid=False, lonaxis_showgrid=False,
                                    bgcolor=settings.BACKGROUND_COLOR,
                                    framecolor=settings.FOREGROUND_COLOR))

    return traces
