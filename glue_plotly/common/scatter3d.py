import numpy as np
from glue.config import settings
from glue.core import BaseData
from glue.utils import ensure_numerical
from matplotlib.colors import to_rgb
from numpy import clip
from plotly.graph_objs import Cone, Scatter3d
from uuid import uuid4

from glue_plotly.common import DEFAULT_FONT, color_info


def dimensions(viewer):
    # when vispy viewer is in "native aspect ratio" mode, scale axes size by data
    if viewer.state.native_aspect:
        width = viewer.state.x_max - viewer.state.x_min
        height = viewer.state.y_max - viewer.state.y_min
        depth = viewer.state.z_max - viewer.state.z_min

    # otherwise, set all axes to be equal size
    else:
        width = 1200  # this 1200 size is arbitrary, could change to any width; just need to scale rest accordingly
        height = 1200
        depth = 1200

    return [width, height, depth]


def projection_type(viewer):
    return "perspective" if viewer.state.perspective_view else "orthographic"


def axis(viewer, ax):
    title = getattr(viewer.state, f'{ax}_att').label
    range = [getattr(viewer.state, f'{ax}_min'), getattr(viewer.state, f'{ax}_max')]
    return dict(
        title=title,
        titlefont=dict(
            family=DEFAULT_FONT,
            size=20,
            color=settings.FOREGROUND_COLOR
        ),
        backgroundcolor=settings.BACKGROUND_COLOR,
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
            size=12,
            color=settings.FOREGROUND_COLOR),
        range=range,
        type='linear',
        rangemode='normal',
        visible=viewer.state.visible_axes
    )


def clipped_data(viewer, layer):
    x = layer.state.layer[viewer.state.x_att]
    y = layer.state.layer[viewer.state.y_att]
    z = layer.state.layer[viewer.state.z_att]

    # Plotly doesn't show anything outside the bounding box
    viewer_state = viewer.state
    mask = (x >= viewer_state.x_min) & (x <= viewer_state.x_max) & \
           (y >= viewer_state.y_min) & (y <= viewer_state.y_max) & \
           (z >= viewer_state.z_min) & (z <= viewer_state.z_max)

    return x[mask], y[mask], z[mask], mask


def size_info(layer, mask):
    state = layer.state

    # set all points to be the same size, with set scaling
    if state.size_mode == 'Fixed':
        return state.size_scaling * state.size

    # scale size of points by set size scaling
    else:
        s = ensure_numerical(state.layer[state.size_attribute][mask].ravel())
        s = ((s - state.size_vmin) /
             (state.size_vmax - state.size_vmin))
        # The following ensures that the sizes are in the
        # range 3 to 30 before the final size scaling.
        clip(s, 0, 1, out=s)
        s *= 0.95
        s += 0.05
        s *= (30 * state.size_scaling)
        return s


def vector_cones(layer, mask, marker, x, y, z, hovertext, hoverinfo):
    legend_group = uuid4().hex
    state = layer.state
    vx = state.layer[state.vx_attribute][mask]
    vy = state.layer[state.vy_attribute][mask]
    vz = state.layer[state.vz_attribute][mask]
    # convert anchor names from glue values to plotly values
    anchor_dict = {'middle': 'center', 'tip': 'tip', 'tail': 'tail'}
    anchor = anchor_dict[state.vector_origin]
    name = state.layer.label + " cones"
    scaling = state.vector_scaling
    cones = []
    vx_v = scaling * vx
    vy_v = scaling * vy
    vz_v = scaling * vz
    if state.color_mode == 'Fixed':
        # get the singular color in rgb format
        rgb_color = [int(c * 256) for c in to_rgb(marker['color'])]
        c = 'rgb{}'.format(tuple(rgb_color))
        colorscale = [[0, c], [1, c]]

        for i in range(len(x)):
            ht = None if hovertext is None else [hovertext[i]]
            cone = Cone(x=[x[i]], y=[y[i]], z=[z[i]],
                        u=[vx_v[i]], v=[vy_v[i]], w=[vz_v[i]],
                        name=name, anchor=anchor, colorscale=colorscale,
                        hoverinfo=hoverinfo, hovertext=ht,
                        showscale=False, legendgroup=legend_group,
                        sizemode="absolute", showlegend=not i, sizeref=1)
            cones.append(cone)
    else:
        for i, c in enumerate(marker['color']):
            ht = None if hovertext is None else [hovertext[i]]
            cone = Cone(x=[x[i]], y=[y[i]], z=[z[i]],
                        u=[vx_v[i]], v=[vy_v[i]], w=[vz_v[i]],
                        name=name, anchor=anchor, colorscale=[[0, c], [1, c]],
                        hoverinfo=hoverinfo, hovertext=ht,
                        showscale=False, legendgroup=legend_group,
                        sizemode="scaled", showlegend=not i, sizeref=1)
            cones.append(cone)

    return cones


def error_bar_info(layer, mask):
    errs = {}
    for ax in ['x', 'y', 'z']:
        err = {}
        if getattr(layer.state, f'{ax}err_visible', False):
            err['type'] = 'data'
            err['array'] = np.absolute(ensure_numerical(
                layer.state.layer[getattr(layer.state, f'{ax}err_attribute')][mask].ravel()))
            err['visible'] = True

            # AFAICT, it seems that we can't have error bars follow the colorscale
            # (if we don't set this and aren't in fixed color mode, they just don't appear).
            # So for now, let's just make them black.
            if layer.state.color_mode != 'Fixed':
                err['color'] = "#000000"
        errs[ax] = err

    return errs


def layout_config(viewer):
    width, height, depth = dimensions(viewer)
    return dict(
        margin=dict(r=50, l=50, b=50, t=50),  # noqa
        width=1200,
        paper_bgcolor=settings.BACKGROUND_COLOR,
        scene=dict(
            xaxis=axis(viewer, 'x'),
            yaxis=axis(viewer, 'y'),
            zaxis=axis(viewer, 'z'),
            camera=dict(
                projection=dict(
                    type=projection_type(viewer)
                )
            ),
            aspectratio=dict(x=1 * viewer.state.x_stretch,
                             y=height / width * viewer.state.y_stretch,
                             z=depth / width * viewer.state.z_stretch),
            aspectmode='manual'
        )
    )


def traces_for_layer(viewer, layer, hover_data=None, add_data_label=True):
    layer_state = layer.state

    x, y, z, mask = clipped_data(viewer, layer)
    marker = dict(color=color_info(layer, mask=mask,
                                   mode_att="color_mode",
                                   cmap_att="cmap_attribute"),
                  size=size_info(layer, mask),
                  opacity=layer_state.alpha,
                  line=dict(width=0))

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

    cones = []
    if layer_state.vector_visible:
        cones = vector_cones(layer, mask, marker, x, y, z, hovertext, hoverinfo)

    err = error_bar_info(layer, mask)

    name = layer.layer.label
    if add_data_label and not isinstance(layer.layer, BaseData):
        name += " ({0})".format(layer.layer.data.label)

    scatter = Scatter3d(x=x, y=y, z=z,
                        error_x=err['x'],
                        error_y=err['y'],
                        error_z=err['z'],
                        mode='markers',
                        marker=marker,
                        hoverinfo=hoverinfo,
                        hovertext=hovertext,
                        name=layer_state.layer.label)

    return [scatter] + cones
