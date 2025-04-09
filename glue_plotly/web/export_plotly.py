
try:
    from chart_studio import plotly
except ImportError:
    plotly = None

from glue.core.layout import Rectangle, snap_to_grid
from glue_plotly.common import (
    base_rectilinear_axis,
    data_count,
    dendrogram,
    histogram,
    layers_to_export,
    profile,
    scatter2d,
)

SYM = {"o": "circle", "s": "square", "+": "cross", "^": "triangle-up",
       "*": "cross"}


def _position_plots(viewers, layout):
    rs = [Rectangle(v.position[0], v.position[1],
                    v.viewer_size[0], v.viewer_size[1])
          for v in viewers]
    right = max(r.x + r.w for r in rs)
    top = max(r.y + r.h for r in rs)
    for r in rs:
        r.x = 1. * r.x / right
        r.y = 1. - 1. * (r.y + r.h) / top
        r.w = 1. * r.w / right
        r.h = 1. * r.h / top

    grid = snap_to_grid(rs, padding=0.05)
    grid = { v: grid[r] for v, r in zip(viewers, rs) }

    for i, plot in enumerate(viewers, 1):
        g = grid[plot]
        xdomain = [g.x, g.x + g.w]
        ydomain = [g.y, g.y + g.h]
        suffix = "" if i == 1 else str(i)

        xax, yax = "xaxis" + suffix, "yaxis" + suffix
        layout[xax].update(domain=xdomain, anchor=yax.replace("axis", ""))
        layout[yax].update(domain=ydomain, anchor=xax.replace("axis", ""))


def _stack_horizontal(layout):
    layout["xaxis"]["domain"] = [0, 0.45]
    layout["xaxis2"]["domain"] = [0.55, 1]
    layout["yaxis2"]["anchor"] = "x2"


def _grid_2x23(layout):
    opts = {
        "xaxis": {"domain": [0, 0.45]},
        "yaxis": {"domain": [0, 0.45]},
        "xaxis2": {"domain": [0.55, 1]},
        "yaxis2": {"domain": [0, 0.45],
                   "anchor": "x2"
                   },
        "xaxis3": {
            "domain": [0, 0.45],
            "anchor": "y3"
        },
        "yaxis3": {
            "domain": [0.55, 1],
        },
        "xaxis4": {
            "domain": [0.55, 1],
            "anchor": "y4",
        },
        "yaxis4": {
            "domain": [0.55, 1],
            "anchor": "x4"
        }
    }
    for k, v in opts.items():
        if k not in layout:
            continue
        layout[k].update(**v)


def _fix_legend_duplicates(traces, _layout):
    """Prevent repeat entries in the legend"""
    seen = set()
    for t in traces:
        key = (t.name, t.marker.color, getattr(t.marker, "symbol", None))
        if key in seen:
            t["showlegend"] = False
        else:
            seen.add(key)


def _color(style):
    r, g, b, a = style.rgba
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return "rgba(%i, %i, %i, %0.1f)" % (r, g, b, a)


def export_scatter(viewer):
    """Export a scatter viewer to a list of Plotly-formatted data dictionaries"""
    traces = []

    layers = layers_to_export(viewer)
    add_data_label = data_count(layers) > 1
    for layer in layers:
        traces += scatter2d.traces_for_layer(viewer, layer.state,
                                             add_data_label=add_data_label)

    xaxis = base_rectilinear_axis(viewer.state, "x")
    yaxis = base_rectilinear_axis(viewer.state, "y")

    return traces, xaxis, yaxis


def export_histogram(viewer):
    """Export a histogram viewer to a list of Plotly-formatted data dictionaries"""
    traces = []
    layers = layers_to_export(viewer)
    add_data_label = data_count(layers) > 1
    for layer in layers:
        traces += histogram.traces_for_layer(viewer.state, layer.state,
                                             add_data_label=add_data_label)

    # For now, set glue_ticks to False
    # TODO: Can we use MathJax (or some other LaTeX formatting) inside Chart Studio?
    # https://github.com/glue-viz/glue-plotly/issues/127
    xaxis = histogram.axis_from_mpl(viewer, "x", glue_ticks=False)
    yaxis = histogram.axis_from_mpl(viewer, "y", glue_ticks=False)

    return traces, xaxis, yaxis


def export_profile(viewer):
    """Export a profile viewer to a list of Plotly-formatted data dictionaries"""
    traces = []
    layers = layers_to_export(viewer)
    add_data_label = data_count(layers) > 1
    for layer in layers:
        traces += profile.traces_for_layer(viewer.state, layer.state,
                                           add_data_label=add_data_label)
    # For now, set glue_ticks to False
    # TODO: Can we use MathJax (or some other LaTeX formatting) inside Chart Studio?
    # https://github.com/glue-viz/glue-plotly/issues/127
    xaxis = profile.axis_from_mpl(viewer, "x", glue_ticks=False)
    yaxis = profile.axis_from_mpl(viewer, "y", glue_ticks=False)

    return traces, xaxis, yaxis


def export_dendrogram(viewer):
    """Export a dendrogram viewer to a list of Plotly-formatted data dictionaries"""
    traces = []
    layers = layers_to_export(viewer)
    add_data_label = data_count(layers) > 1
    for layer in layers:
        data = layer.mpl_artists[0].get_xydata()
        trace = dendrogram.trace_for_layer(layer.state, data,
                                           add_data_label=add_data_label)
        traces.append(trace)

    config = dendrogram.layout_config_from_mpl(viewer)

    return traces, config["xaxis"], config["yaxis"]


def build_plotly_call(app):
    """"Export a glue session to data for sending to Chart Studio.

    This function exports the session to a list of Plotly-formatted dictionaries and a
    dictionary of keyword arguments. Currently, the returned dictionary of Plotly
    keyword arguments is empty.
    """
    args = []
    layout = {"showlegend": True, "barmode": "overlay", "bargap": 0,
              "title": "Autogenerated by Glue"}

    ct = 1
    for tab in app.viewers:
        for viewer in tab:
            if hasattr(viewer, "__plotly__"):
                p, xaxis, yaxis = viewer.__plotly__()
            else:
                p, xaxis, yaxis = DISPATCH[type(viewer)](viewer)

            xaxis["zeroline"] = False
            yaxis["zeroline"] = False

            suffix = "" if ct == 1 else f"{ct}"
            layout["xaxis" + suffix] = xaxis
            layout["yaxis" + suffix] = yaxis
            if ct > 1:
                yaxis["anchor"] = "x" + suffix
                for item in p:
                    item.update(xaxis="x" + suffix, yaxis="y" + suffix)
            ct += 1
            args.extend(p)

    _position_plots([v for tab in app.viewers for v in tab], layout)
    _fix_legend_duplicates(args, layout)

    return [dict(data=args, layout=layout)], {}


def can_save_plotly(application):
    """
    Check whether an application can be exported to Plotly

    Raises an exception if not
    """
    if not plotly:
        msg = (
            "Plotly Export requires the Plotly Python library. "
            "Please install first"
        )
        raise ValueError(msg)

    for tab in application.viewers:
        for viewer in tab:
            if hasattr(viewer, "__plotly__"):
                continue

            if not isinstance(viewer, tuple(DISPATCH)):
                msg = f"Plotly Export cannot handle viewer: {type(viewer)}"
                raise TypeError(msg)

    if len(application.viewers) != 1:
        msg = (
            "Plotly Export only supports a single tab. "
            "Please close other tabs to export"
        )
        raise ValueError(msg)

    nplot = sum(len(t) for t in application.viewers)
    if nplot == 0:
        msg = "Plotly Export requires at least one plot"
        raise ValueError(msg)

    max_plots = 4
    if nplot > max_plots:
        msg = "Plotly Export supports at most 4 plots"
        raise ValueError(msg)


DISPATCH = {}
