from __future__ import absolute_import, division, print_function

import numpy as np

from qtpy import compat
from glue.config import viewer_tool, settings
from glue.core import Subset

from ..utils import ticks_values

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

from plotly.offline import plot
import plotly.graph_objs as go

DEFAULT_FONT = 'Arial, sans-serif'


@viewer_tool
class PlotlyProfile1DExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotlyprofile'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

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

                x, y = layer_state.profile
                if self.viewer.state.normalize:
                    y = layer_state.normalize_values(y)
                line = dict(width=2*layer_state.linewidth)
                line['shape'] = 'hvh' if layer_state.as_steps else 'linear'

                if layer_state.color != '0.35':
                    line['color'] = layer_state.color
                else:
                    line['color'] = 'gray'

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

                profile_info = dict(hoverinfo='skip', line=line, opacity=layer_state.alpha, name=label, x=x, y=y)
                fig.add_scatter(**profile_info)

        plot(fig, include_mathjax='cdn', filename=filename, auto_open=False)
