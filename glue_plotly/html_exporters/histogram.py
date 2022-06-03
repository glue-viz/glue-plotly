from __future__ import absolute_import, division, print_function

import numpy as np

from qtpy import compat
from glue.config import viewer_tool, settings

from glue.core import DataCollection, Data

from .. import save_hover

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

from plotly.offline import plot
import plotly.graph_objs as go
from glue.core.qt.dialogs import warn

DEFAULT_FONT = 'Arial, sans-serif'


@viewer_tool
class PlotlyHistogram1DExport(Tool):

    icon = PLOTLY_LOGO
    tool_id = 'save:plotlyhist'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        # grab hover info
        dc_hover = DataCollection()
        for layer in self.viewer.layers:
            layer_state = layer.state
            if layer_state.visible and layer.enabled:
                data = Data(label=layer_state.layer.label)
                for component in layer_state.layer.components:
                    data[component.label] = np.ones(10)
                dc_hover.append(data)

        checked_dictionary = {}

        # figure out which hover info user wants to display
        for layer in self.viewer.layers:
            layer_state = layer.state
            if layer_state.visible and layer.enabled:
                checked_dictionary[layer_state.layer.label] = np.zeros((len(layer_state.layer.components))).astype(bool)

        dialog = save_hover.SaveHoverDialog(data_collection=dc_hover, checked_dictionary=checked_dictionary)
        proceed = warn('Histogram plotly may look different', 'Plotly and Matlotlib binning methods differ and your graph may look different when exported. Do you want to proceed?',
                    default='Cancel', setting='SHOW_WARN_PROFILE_DUPLICATE')
        if not proceed:
            return
        dialog.exec_()

        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")

        width, height = self.viewer.figure.get_size_inches()*self.viewer.figure.dpi

        # set the aspect ratio of the axes, the tick label size, the axis label
        # sizes, and the axes limits
        layout_config = dict(
            margin=dict(r=50, l=50, b=50, t=50),  # noqa
            width=1200,
            height=1200*height/width,  # scale axis correctly
            paper_bgcolor=settings.BACKGROUND_COLOR,
            plot_bgcolor=settings.BACKGROUND_COLOR
        )

        x_axis = dict(
            title=self.viewer.axes.get_xlabel(),
            titlefont=dict(
                family=DEFAULT_FONT,
                size=2*self.viewer.axes.xaxis.get_label().get_size(),
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
                size=1.5*self.viewer.axes.xaxis.get_ticklabels()[
                    0].get_fontsize(),
                color=settings.FOREGROUND_COLOR),
            range=[self.viewer.state.x_min, self.viewer.state.x_max]
        )
        y_axis = dict(
            title=self.viewer.axes.get_ylabel(),
            titlefont=dict(
                family=DEFAULT_FONT,
                size=2*self.viewer.axes.yaxis.get_label().get_size(),
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
                size=1.5*self.viewer.axes.yaxis.get_ticklabels()[
                    0].get_fontsize(),
                color=settings.FOREGROUND_COLOR),
        )
        layout_config.update(xaxis=x_axis, yaxis=y_axis)

        layout = go.Layout(**layout_config)

        fig = go.Figure(layout=layout)

        for layer in self.viewer.layers:

            layer_state = layer.state

            if layer_state.visible and layer.enabled:

                x = layer_state.layer[self.viewer.state.x_att]

                marker = {}

                # set all bars to be the same color
                if layer_state.color != '0.35':
                        marker['color'] = layer_state.color
                else:
                    marker['color'] = 'gray'

                # set the opacity
                marker['opacity'] = layer_state.alpha

                # check whether to show cumulative
                cumulative = {}
                if self.viewer.state.cumulative:
                    cumulative['currentbin'] = 'include'
                    cumulative['enabled'] = True

                # set log
                if self.viewer.state.x_log:
                    fig.update_xaxes(type='log', dtick=1, minor_ticks='outside',
                        range=[np.log10(self.viewer.state.x_min), np.log10(self.viewer.state.x_max)]
                    )
                if self.viewer.state.y_log:
                    fig.update_yaxes(type='log', dtick=1, minor_ticks='outside',
                        range=[np.log10(self.viewer.state.y_min), np.log10(self.viewer.state.y_max)]
                    )

                # set xbins
                # when the max bin edge is the same as the max x value, plotly excludes this value
                # so there is always one less in the frequency if these numbers are equal
                if self.viewer.state.x_log:
                    start_val = np.log10(self.viewer.state.hist_x_min)
                    end_val = self.viewer.state.hist_x_max
                    # end_val += end_val * 0.001
                    end_val *= np.log10(end_val)
                else:
                    start_val = self.viewer.state.hist_x_min
                    end_val = self.viewer.state.hist_x_max
                    # end_val += end_val * 0.001
                print(self.viewer.state.hist_n_bin)
                xbins = dict(
                    start=start_val,
                    end=end_val,
                    size=(self.viewer.state.hist_x_max - self.viewer.state.hist_x_min) / 
                        self.viewer.state.hist_n_bin
                )

                # add hover info to layer

                if np.sum(dialog.checked_dictionary[layer_state.layer.label]) == 0:
                    hoverinfo = 'skip'
                    hovertext = None
                else:
                    hoverinfo = 'text'
                    hovertext = ["" for i in range((layer_state.layer.shape[0]))]
                    for i in range(0, len(layer_state.layer.components)):
                        if dialog.checked_dictionary[layer_state.layer.label][i]:
                            hover_data = layer_state.layer[layer_state.layer.components[i].label]
                            for k in range(0, len(hover_data)):
                                hovertext[k] = (hovertext[k] + "{}: {} <br>"
                                                .format(layer_state.layer.components[i].label,
                                                        hover_data[k]))

                # add layer to dict
                hist_info = dict(
                    x=x,
                    nbinsx=self.viewer.state.hist_n_bin,
                    xbins=xbins,
                    marker=marker,
                    cumulative=cumulative,
                    hoverinfo=hoverinfo,
                    hovertext=hovertext,
                    name=layer_state.layer.label,
                    autobinx=False
                )
                fig.add_histogram(**hist_info)

        plot(fig, filename=filename, auto_open=False)
