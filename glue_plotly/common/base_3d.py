import re

from glue.config import settings
from glue_plotly.common import DEFAULT_FONT


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
    return "perspective" if getattr(viewer_state, "perspective_view", True) else "orthographic"


def get_resolution(viewer_state):
    try:
        from glue_vispy_viewers.volume.viewer_state import Vispy3DVolumeViewerState
        if isinstance(viewer_state, Vispy3DVolumeViewerState):
            return viewer_state.resolution
    except ImportError:
        pass

    try:
        from glue_jupyter.common.state3d import VolumeViewerState
        if isinstance(viewer_state, VolumeViewerState):
            resolutions = tuple(getattr(state, 'max_resolution', None) for state in viewer_state.layers)
            return max((res for res in resolutions if res is not None), default=256)
    except ImportError:
        pass

    return 256


# TODO: Update other methods to not rely on these being reversed
def bounds(viewer_state, with_resolution=False):
    bds = [(viewer_state.z_min, viewer_state.z_max),
           (viewer_state.y_min, viewer_state.y_max),
           (viewer_state.x_min, viewer_state.x_max)]
    if with_resolution:
        resolution = get_resolution(viewer_state)
        return [(*b, resolution) for b in bds]

    return bds


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


def bbox_mask(viewer_state, x, y, z):
    return (x >= viewer_state.x_min) & (x <= viewer_state.x_max) & \
           (y >= viewer_state.y_min) & (y <= viewer_state.y_max) & \
           (z >= viewer_state.z_min) & (z <= viewer_state.z_max)


def clipped_data(viewer_state, layer_state):
    x = layer_state.layer[viewer_state.x_att]
    y = layer_state.layer[viewer_state.y_att]
    z = layer_state.layer[viewer_state.z_att]

    # Plotly doesn't show anything outside the bounding box
    mask = bbox_mask(viewer_state, x, y, z)

    return x[mask], y[mask], z[mask], mask


def plotly_up_from_vispy(vispy_up):
    regex = re.compile("(\\+|-)(x|y|z)")
    up = {"x": 0, "y": 0, "z": 0}
    m = regex.match(vispy_up)
    if m is not None and len(m.groups()) == 2:
        sign = 1 if m.group(1) == "+" else -1
        up[m.group(2)] = sign
    return up


def layout_config(viewer_state):
    width, height, depth = dimensions(viewer_state)
    x_stretch = getattr(viewer_state, "x_stretch", 1.)
    y_stretch = getattr(viewer_state, "y_stretch", 1.)
    z_stretch = getattr(viewer_state, "z_stretch", 1.)
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
                ),
                # Currently there's no way to change this in glue
                up=plotly_up_from_vispy("+z")
            ),
            aspectratio=dict(x=1 * x_stretch,
                             y=height / width * y_stretch,
                             z=depth / width * z_stretch),
            aspectmode='manual'
        )
    )
