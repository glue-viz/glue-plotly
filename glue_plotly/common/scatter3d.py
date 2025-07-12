from uuid import uuid4

import numpy as np
from matplotlib.colors import to_rgb
from numpy import clip
from plotly.graph_objs import Cone, Scatter3d

from glue.core import BaseData
from glue.utils import ensure_numerical
from glue_plotly.common import color_info, sanitize
from glue_plotly.common.base_3d import bbox_mask

try:
    from glue_vispy_viewers.scatter.layer_state import ScatterLayerState
except ImportError:
    ScatterLayerState = type(None)


def size_info(layer_state, mask, size_att="size_attribute"):

    # set all points to be the same size, with set scaling
    if layer_state.size_mode == "Fixed":
        return layer_state.size_scaling * layer_state.size

    # scale size of points by set size scaling
    size_att = getattr(layer_state, size_att)
    s = ensure_numerical(layer_state.layer[size_att][mask].ravel())
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
    anchor_dict = {"middle": "center", "tip": "tip", "tail": "tail"}
    anchor = anchor_dict[layer_state.vector_origin]
    name = layer_state.layer.label + " cones"
    scaling = layer_state.vector_scaling
    cones = []
    vx_v = scaling * vx
    vy_v = scaling * vy
    vz_v = scaling * vz
    if layer_state.color_mode == "Fixed":
        # get the singular color in rgb format
        rgb_color = [int(c * 256) for c in to_rgb(marker["color"])]
        c = f"rgb{tuple(rgb_color)}"
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
        for i, c in enumerate(marker["color"]):
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
    for ax in ["x", "y", "z"]:
        err = {}
        if getattr(layer_state, f"{ax}err_visible", False):
            err["type"] = "data"
            err_att = getattr(layer_state, f"{ax}err_attribute")
            err["array"] = np.absolute(ensure_numerical(
                layer_state.layer[err_att][mask].ravel()))
            err["visible"] = True

            # AFAICT, it seems that we can't have error bars follow the colorscale
            # (if we don't set this and aren't in fixed color mode,
            # they just don't appear).
            # So for now, let's just make them black.
            if layer_state.color_mode != "Fixed":
                err["color"] = "#000000"
        errs[ax] = err

    return errs


_IPYVOLUME_GEOMETRY_SYMBOLS = {
    "sphere": "circle",
    "box": "square",
    "diamond": "diamond",
    "circle2d": "circle",
}


def symbol_for_geometry(geometry: str) -> str:
    symbol = _IPYVOLUME_GEOMETRY_SYMBOLS.get(geometry)
    if symbol is not None:
        return symbol
    msg = f"Invalid geometry: {geometry}"
    raise ValueError(msg)


def traces_for_layer(viewer_state, layer_state, hover_data=None, add_data_label=True):

    x = layer_state.layer[viewer_state.x_att]
    y = layer_state.layer[viewer_state.y_att]
    z = layer_state.layer[viewer_state.z_att]

    vispy_layer_state = isinstance(layer_state, ScatterLayerState)
    cmap_mode_attr = "color_mode" if vispy_layer_state else "cmap_mode"
    cmap_attr = "cmap_attribute" if vispy_layer_state else "cmap_att"
    size_attr = "size_attribute" if vispy_layer_state else "size_att"
    arrs = [x, y, z]
    if getattr(layer_state, cmap_mode_attr) == "Linear":
        cvals = layer_state.layer[getattr(layer_state, cmap_attr)].copy()
        arrs.append(cvals)
    if layer_state.size_mode == "Linear":
        svals = layer_state.layer[getattr(layer_state, size_attr)].copy()
        arrs.append(svals)

    mask, _ = sanitize(*arrs)
    bounds_mask = bbox_mask(viewer_state, x, y, z)
    mask &= bounds_mask
    x, y, z = x[mask], y[mask], z[mask]

    marker = dict(color=color_info(layer_state, mask=mask,
                                   mode_att=cmap_mode_attr,
                                   cmap_att=cmap_attr),
                  size=size_info(layer_state, mask, size_att=size_attr),
                  opacity=layer_state.alpha,
                  line=dict(width=0))

    if hasattr(layer_state, "geo"):
        symbol = symbol_for_geometry(layer_state.geo)
        marker["symbol"] = symbol

    if hover_data is None or np.sum(hover_data) == 0:
        hoverinfo = "skip"
        hovertext = None
    else:
        hoverinfo = "text"
        hovertext = ["" for _ in range(mask.size)]
        for component in layer_state.layer.components:
            label = component.label
            if hover_data.get(label, False):
                hover_values = layer_state.layer[label][mask]
                for k in range(len(hover_values)):
                    hovertext[k] = (hovertext[k] + f"{label}: {hover_values[k]} <br>"
                                    )

    cones = []
    if layer_state.vector_visible:
        cones = vector_cones(layer_state, mask, marker, x, y, z, hovertext, hoverinfo)

    err = error_bar_info(layer_state, mask)

    name = layer_state.layer.label
    if add_data_label and not isinstance(layer_state.layer, BaseData):
        name += f" ({layer_state.layer.data.label})"

    scatter = Scatter3d(x=x, y=y, z=z,
                        error_x=err["x"],
                        error_y=err["y"],
                        error_z=err["z"],
                        mode="markers",
                        marker=marker,
                        hoverinfo=hoverinfo,
                        hovertext=hovertext,
                        name=layer_state.layer.label)

    return [scatter] + cones
