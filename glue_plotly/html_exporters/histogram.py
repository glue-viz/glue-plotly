from __future__ import absolute_import, division, print_function

import numpy as np

from qtpy import compat
from glue.config import viewer_tool, settings
from glue.core import Subset
from glue.utils.qt import messagebox_on_error

from ..utils import ticks_values

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_ERROR_MESSAGE, PLOTLY_LOGO

from plotly.offline import plot
import plotly.graph_objs as go

DEFAULT_FONT = 'Arial, sans-serif'


@viewer_tool
class PlotlyHistogram1DExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotlyhist'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    @messagebox_on_error(PLOTLY_ERROR_MESSAGE)
    def activate(self):
        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")

        width, height = self.viewer.figure.get_size_inches() * self.viewer.figure.dpi

        # set the aspect ratio of the axes, the tick label size, the axis label
        # sizes, and the axes limits
        layout_config = dict(
            margin=dict(r=50, l=50, b=50, t=50),  # noqa
            width=1200,
            height=1200 * height / width,  # scale axis correctly
            paper_bgcolor=settings.BACKGROUND_COLOR,
            plot_bgcolor=settings.BACKGROUND_COLOR,
            barmode="overlay",
            bargap=0
        )

        x_axis = dict(
            title=self.viewer.axes.get_xlabel(),
            titlefont=dict(
                family=DEFAULT_FONT,
                size=2 * self.viewer.axes.xaxis.get_label().get_size(),
                color=settings.FOREGROUND_COLOR
            ),
            showspikes=False,
            linecolor=settings.FOREGROUND_COLOR,
            tickcolor=settings.FOREGROUND_COLOR,
            mirror=True,
            ticks='outside',
            showline=True,
            showgrid=False,
            showticklabels=True,
            tickfont=dict(
                family=DEFAULT_FONT,
                size=1.5 * self.viewer.axes.xaxis.get_ticklabels()[
                    0].get_fontsize(),
                color=settings.FOREGROUND_COLOR),
            range=[self.viewer.state.x_min, self.viewer.state.x_max]
        )
        y_axis = dict(
            title=self.viewer.axes.get_ylabel(),
            titlefont=dict(
                family=DEFAULT_FONT,
                size=2 * self.viewer.axes.yaxis.get_label().get_size(),
                color=settings.FOREGROUND_COLOR),
            showgrid=False,
            showspikes=False,
            linecolor=settings.FOREGROUND_COLOR,
            tickcolor=settings.FOREGROUND_COLOR,
            zeroline=False,
            mirror=True,
            ticks='outside',
            showline=True,
            range=[self.viewer.state.y_min, self.viewer.state.y_max],
            showticklabels=True,
            tickfont=dict(
                family=DEFAULT_FONT,
                size=1.5 * self.viewer.axes.yaxis.get_ticklabels()[
                    0].get_fontsize(),
                color=settings.FOREGROUND_COLOR),
        )

        axes = self.viewer.axes
        xvals, xtext = ticks_values(axes, 'x')
        if xvals and xtext:
            x_axis.update(tickmode='array', tickvals=xvals, ticktext=xtext)
        yvals, ytext = ticks_values(axes, 'y')
        if yvals and ytext:
            y_axis.update(tickmode='array', tickvals=yvals, ticktext=ytext)

        layout_config.update(xaxis=x_axis, yaxis=y_axis)

        layout = go.Layout(**layout_config)

        fig = go.Figure(layout=layout)

        for layer in self.viewer.layers:

            layer_state = layer.state

            if layer_state.visible and layer.enabled:

                # The x values should be at the midpoints between successive pairs of edge values
                edges, y = layer_state.histogram
                x = [0.5 * (edges[i] + edges[i + 1]) for i in range(len(edges) - 1)]

                marker = {}

                # set all bars to be the same color
                if layer_state.color != '0.35':
                    marker['color'] = layer_state.color
                else:
                    marker['color'] = 'gray'

                # set the opacity and remove bar borders
                marker['opacity'] = layer_state.alpha
                marker['line'] = dict(width=0)

                # set log
                if self.viewer.state.x_log:
                    fig.update_xaxes(type='log', dtick=1, minor_ticks='outside',
                                     range=[np.log10(self.viewer.state.x_min), np.log10(self.viewer.state.x_max)]
                                     )
                if self.viewer.state.y_log:
                    fig.update_yaxes(type='log', dtick=1, minor_ticks='outside',
                                     range=[np.log10(self.viewer.state.y_min), np.log10(self.viewer.state.y_max)]
                                     )

                label = layer.layer.label
                if isinstance(layer.layer, Subset):
                    label += " ({0})".format(layer.layer.data.label)

                hist_info = dict(hoverinfo="skip", marker=marker, name=label)
                if self.viewer.state.x_log:
                    for i in range(len(x)):
                        hist_info.update(
                            legendgroup=label,
                            showlegend=i == 0,
                            x=[x[i]],
                            y=[y[i]],
                            width=edges[i + 1] - edges[i],
                        )
                        fig.add_bar(**hist_info)
                else:
                    hist_info.update(
                        x=x,
                        y=y,
                        width=edges[1] - edges[0],
                    )
                    fig.add_bar(**hist_info)

        plot(fig, include_mathjax='cdn', filename=filename, auto_open=False)
