import numpy as np
from glue.config import settings
from glue.core import BaseData
from glue.utils import ensure_numerical
from matplotlib.colors import to_rgb
from numpy import clip
from plotly.graph_objs import Cone, Scatter3d
from uuid import uuid4

from glue_plotly.common import DEFAULT_FONT, color_info


def dimensions(viewer_state):
    # when vispy viewer is in "native aspect ratio" mode, scale axes size by data
    if viewer_state.native_aspect:
        width = viewer_state.x_max - viewer_state.x_min
        height = viewer_state.y_max - viewer_state.y_min
        depth = viewer_state.z_max - viewer_state.z_min

    # otherwise, set all axes to be equal size
    else:
        width = 1200  # this 1200 size is arbitrary, could change to any width; just need to scale rest accordingly
        height = 1200
        depth = 1200

    return [width, height, depth]


def projection_type(viewer_state):
    return "perspective" if viewer_state.perspective_view else "orthographic"


def axis(viewer_state, ax):
    title = getattr(viewer_state, f'{ax}_att').label
    range = [getattr(viewer_state, f'{ax}_min'), getattr(viewer_state, f'{ax}_max')]
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
        visible=viewer_state.visible_axes
    )


def clipped_data(viewer_state, layer_state):
    x = layer_state.layer[viewer_state.x_att]
    y = layer_state.layer[viewer_state.y_att]
    z = layer_state.layer[viewer_state.z_att]

    # Plotly doesn't show anything outside the bounding box
    mask = (x >= viewer_state.x_min) & (x <= viewer_state.x_max) & \
           (y >= viewer_state.y_min) & (y <= viewer_state.y_max) & \
           (z >= viewer_state.z_min) & (z <= viewer_state.z_max)

    return x[mask], y[mask], z[mask], mask


def size_info(layer_state, mask):

    # set all points to be the same size, with set scaling
    if layer_state.size_mode == 'Fixed':
        return layer_state.size_scaling * layer_state.size

    # scale size of points by set size scaling
    else:
        s = ensure_numerical(layer_state.layer[layer_state.size_attribute][mask].ravel())
        s = ((s - layer_state.size_vmin) /
             (layer_state.size_vmax - layer_state.size_vmin))
        # The following ensures that the sizes are in the
        # range 3 to 30 before the final size scaling.
        clip(s, 0, 1, out=s)
        s *= 0.95
        s += 0.05
        s *= (30 * layer_state.size_scaling)
        return s


def vector_cones(layer_state, mask, marker, x, y, z, hovertext, hoverinfo):
    legend_group = uuid4().hex
    vx = layer_state.layer[layer_state.vx_attribute][mask]
    vy = layer_state.layer[layer_state.vy_attribute][mask]
    vz = layer_state.layer[layer_state.vz_attribute][mask]
    # convert anchor names from glue values to plotly values
    anchor_dict = {'middle': 'center', 'tip': 'tip', 'tail': 'tail'}
    anchor = anchor_dict[layer_state.vector_origin]
    name = layer_state.layer.label + " cones"
    scaling = layer_state.vector_scaling
    cones = []
    vx_v = scaling * vx
    vy_v = scaling * vy
    vz_v = scaling * vz
    if layer_state.color_mode == 'Fixed':
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


def error_bar_info(layer_state, mask):
    errs = {}
    for ax in ['x', 'y', 'z']:
        err = {}
        if getattr(layer_state, f'{ax}err_visible', False):
            err['type'] = 'data'
            err['array'] = np.absolute(ensure_numerical(
                layer_state.layer[getattr(layer_state, f'{ax}err_attribute')][mask].ravel()))
            err['visible'] = True

            # AFAICT, it seems that we can't have error bars follow the colorscale
            # (if we don't set this and aren't in fixed color mode, they just don't appear).
            # So for now, let's just make them black.
            if layer_state.color_mode != 'Fixed':
                err['color'] = "#000000"
        errs[ax] = err

    return errs


def layout_config(viewer_state):
    width, height, depth = dimensions(viewer_state)
    return dict(
        margin=dict(r=50, l=50, b=50, t=50),  # noqa
        width=1200,
        paper_bgcolor=settings.BACKGROUND_COLOR,
        scene=dict(
            xaxis=axis(viewer_state, 'x'),
            yaxis=axis(viewer_state, 'y'),
            zaxis=axis(viewer_state, 'z'),
            camera=dict(
                projection=dict(
                    type=projection_type(viewer_state)
                )
            ),
            aspectratio=dict(x=1 * viewer_state.x_stretch,
                             y=height / width * viewer_state.y_stretch,
                             z=depth / width * viewer_state.z_stretch),
            aspectmode='manual'
        )
    )


def traces_for_layer(viewer_state, layer_state, hover_data=None, add_data_label=True):

    x, y, z, mask = clipped_data(viewer_state, layer_state)
    marker = dict(color=color_info(layer_state, mask=mask,
                                   mode_att="color_mode",
                                   cmap_att="cmap_attribute"),
                  size=size_info(layer_state, mask),
                  opacity=layer_state.alpha,
                  line=dict(width=0))

    if hover_data is None or np.sum(hover_data) == 0:
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
        cones = vector_cones(layer_state, mask, marker, x, y, z, hovertext, hoverinfo)

    err = error_bar_info(layer_state, mask)

    name = layer_state.layer.label
    if add_data_label and not isinstance(layer_state.layer, BaseData):
        name += " ({0})".format(layer_state.layer.data.label)

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
