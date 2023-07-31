from numpy import log10

from glue.config import settings

from glue_plotly.common import DEFAULT_FONT
from glue_plotly.utils import cleaned_labels

def dimensions(viewer):
    return viewer.figure.get_size_inches() * viewer.figure.dpi


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


def base_rectilinear_axis(viewer, axis):
    title = getattr(viewer.axes, f'get_{axis}label')()
    ax = getattr(viewer.axes, f'{axis}axis')
    range = [getattr(viewer.state, f'{axis}_min'), getattr(viewer.state, f'{axis}_max')]
    log = getattr(viewer.state, f'{axis}_log')
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
        axis_dict.update(dtick=1, minor_ticks='outside',
                         range=list(log10(range)))
    return axis_dict


def ticks_values(axes, axis):
    index = 1 if axis == 'y' else 0
    minor_getters = [axes.get_xminorticklabels, axes.get_yminorticklabels]
    minor_ticks = minor_getters[index]()
    if not (minor_ticks and any(t.get_text() for t in minor_ticks)):
        return [], []
    major_getters = [axes.get_xticklabels, axes.get_yticklabels]
    major_ticks = major_getters[index]()
    vals, text = [], []
    for tick in major_ticks + minor_ticks:
        txt = tick.get_text()
        if txt:
            vals.append(tick.get_position()[index])
            text.append(txt)
        text = cleaned_labels(text)
    return vals, text


