import numpy as np

from glue.config import settings

DEFAULT_FONT = 'Arial, sans-serif'


def base_layout_config(viewer, **kwargs):
    # set the aspect ratio of the axes, the tick label size, the axis label
    # sizes, and the axes limits
    width, height = viewer.figure.get_size_inches() * viewer.figure.dpi

    config = dict(
        margin=dict(r=50, l=50, b=50, t=50),  # noqa
        width=1200,
        height=1200 * height / width,  # scale axis correctly
        paper_bgcolor=settings.BACKGROUND_COLOR,
        plot_bgcolor=settings.BACKGROUND_COLOR
    )
    config.update(kwargs)
    return config


def cartesian_axis(viewer, axis='x'):
    x_axis = axis == 'x'
    title = viewer.axes.get_xlabel() if x_axis else viewer.axes.get_ylabel()
    ax = viewer.axes.xaxis if x_axis else viewer.axes.yaxis
    range = [viewer.state.x_min, viewer.state.x_max] if x_axis \
        else [viewer.state.y_min, viewer.state.y_max]
    log = viewer.state.x_log if x_axis else viewer.state.y_log
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

    return tuple(a[mask].ravel() for a in arrays)
