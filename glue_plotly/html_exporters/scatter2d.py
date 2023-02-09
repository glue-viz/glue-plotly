from __future__ import absolute_import, division, print_function

from math import pi
import numpy as np
import matplotlib.colors as colors
from matplotlib.colors import Normalize

from qtpy import compat
from qtpy.QtWidgets import QDialog

from glue.config import viewer_tool, settings
from glue.core import DataCollection, Data
from glue.utils import ensure_numerical
from glue.utils.qt import messagebox_on_error
from glue.viewers.scatter.layer_artist import plot_colored_line

from .. import save_hover

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool
from glue.core.qt.dialogs import warn

from glue_plotly import PLOTLY_ERROR_MESSAGE, PLOTLY_LOGO

from plotly.offline import plot
import plotly.graph_objs as go
import plotly.figure_factory as ff

DEFAULT_FONT = 'Arial, sans-serif'

SHOW_PLOTLY_VECTORS_2D_DIFFERENT = 'SHOW_PLOTLY_2D_VECTORS_DIFFERENT'
settings.add(SHOW_PLOTLY_VECTORS_2D_DIFFERENT, True)

@viewer_tool
class PlotlyScatter2DStaticExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotly2d'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def _adjusted_vector_points(self, origin, scale, x, y, vx, vy):
        vx = scale * vx
        vy = scale * vy
        if origin == 'tail':
            return x, y
        elif origin == 'middle':
            return x - 0.5 * vx, y - 0.5 * vy
        else: # tip
            return x - vx, y - vy

    @messagebox_on_error(PLOTLY_ERROR_MESSAGE)
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
        result = dialog.exec_()
        if result == QDialog.Rejected:
            return

        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")
        if not filename:
            return

        width, height = self.viewer.figure.get_size_inches() * self.viewer.figure.dpi

        polar = getattr(self.viewer.state, 'using_polar', False)
        degrees = polar and self.viewer.state.using_degrees

        # other projections
        proj = self.viewer.state.plot_mode
        proj_type = 'azimuthal equal area' if proj == 'lambert' else proj

        # set the aspect ratio of the axes, the tick label size, the axis label
        # sizes, and the axes limits
        layout_config = dict(
            margin=dict(r=50, l=50, b=50, t=50),  # noqa
            width=1200,
            height=1200 * height / width,  # scale axis correctly
            paper_bgcolor=settings.BACKGROUND_COLOR,
            plot_bgcolor=settings.BACKGROUND_COLOR
        )

        if polar:
            angle_unit = 'degrees' if degrees else 'radians'
            theta_prefix = ''
            if self.viewer.state.x_axislabel:
                theta_prefix = '{0}='.format(self.viewer.state.x_axislabel)
            angular_axis = dict(
                type='linear',
                thetaunit=angle_unit,
                showticklabels=True,
                showtickprefix='first',
                tickprefix=theta_prefix,
                tickfont=dict(
                    family=DEFAULT_FONT,
                    size=1.5 * self.viewer.axes.xaxis.get_ticklabels()[
                        0].get_fontsize(),
                    color=settings.FOREGROUND_COLOR),
                linecolor=settings.FOREGROUND_COLOR,
                gridcolor=settings.FOREGROUND_COLOR
            )
            radial_axis = dict(
                type='linear',
                range=[self.viewer.state.y_min, self.viewer.state.y_max],
                showticklabels=True,
                tickmode='array',
                tickvals=self.viewer.axes.yaxis.get_majorticklocs(),
                ticktext=['<i>{0}</i>'.format(t.get_text()) for t in self.viewer.axes.yaxis.get_majorticklabels()],
                angle=22.5,
                tickangle=22.5,
                showline=False,
                tickfont=dict(
                    family=DEFAULT_FONT,
                    size=1.5 * self.viewer.axes.yaxis.get_ticklabels()[
                        0].get_fontsize(),
                    color=settings.FOREGROUND_COLOR),
                linecolor=settings.FOREGROUND_COLOR,
                gridcolor=settings.FOREGROUND_COLOR
            )
            polar_layout = go.layout.Polar(angularaxis=angular_axis, radialaxis=radial_axis,
                                           bgcolor=settings.BACKGROUND_COLOR)
            layout_config.update(polar=polar_layout)

        else:
            angle_unit = None
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
                zeroline=False,
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
            layout_config.update(xaxis=x_axis, yaxis=y_axis)

        layout = go.Layout(**layout_config)

        fig = go.Figure(layout=layout)

        for layer in self.viewer.layers:

            layer_state = layer.state

            if layer_state.visible and layer.enabled:

                x = layer_state.layer[self.viewer.state.x_att].copy()
                y = layer_state.layer[self.viewer.state.y_att].copy()

                marker = {}

                layer_color = layer_state.color
                if layer_color == '0.35':
                    layer_color = 'gray'

                # set all points to be the same color
                if layer_state.cmap_mode == 'Fixed':
                    marker['color'] = layer_color

                # color by some attribute
                else:
                    if layer_state.cmap_vmin > layer_state.cmap_vmax:
                        cmap = layer_state.cmap.reversed()
                        norm = Normalize(
                            vmin=layer_state.cmap_vmax, vmax=layer_state.cmap_vmin)
                    else:
                        cmap = layer_state.cmap
                        norm = Normalize(
                            vmin=layer_state.cmap_vmin, vmax=layer_state.cmap_vmax)

                    # most matplotlib colormaps aren't recognized by plotly, so we convert manually to a hex code
                    rgba_list = [
                        cmap(norm(point)) for point in layer_state.layer[layer_state.cmap_att].copy()]
                    rgb_str = [r'{}'.format(colors.rgb2hex(
                        (rgba[0], rgba[1], rgba[2]))) for rgba in rgba_list]
                    marker['color'] = rgb_str

                # set all points to be the same size, with some arbitrary scaling
                if layer_state.size_mode == 'Fixed':
                    marker['size'] = 2 * layer_state.size_scaling * layer_state.size

                # scale size of points by set size scaling
                else:
                    s = ensure_numerical(layer_state.layer[layer_state.size_att].ravel())
                    s = ((s - layer_state.size_vmin) /
                         (layer_state.size_vmax - layer_state.size_vmin))
                    # The following ensures that the sizes are in the
                    # range 3 to 30 before the final size scaling.
                    np.clip(s, 0, 1, out=s)
                    s *= 0.95
                    s += 0.05
                    s *= (30 * layer_state.size_scaling)
                    marker['size'] = s

                # set the opacity
                marker['opacity'] = layer_state.alpha

                # check whether or not to fill circles

                if not layer_state.fill:
                    marker['color'] = 'rgba(0,0,0,0)'
                    marker['line'] = dict(width=1,
                                          color=layer_state.color)

                else:
                    # remove default white border around points
                    marker['line'] = dict(width=0)

                # add vectors
                if layer_state.vector_visible and layer_state.vector_scaling > 0.1:
                    proceed = warn('Arrows may look different',
                                   'Plotly and Matlotlib vector graphics differ and your graph may look different '
                                   'when exported. Do you want to proceed?',
                                   default='Cancel', setting=SHOW_PLOTLY_VECTORS_2D_DIFFERENT)
                    if not proceed:
                        return
                    vx = layer_state.layer[layer_state.vx_att]
                    vy = layer_state.layer[layer_state.vy_att]
                    if layer_state.vector_mode == 'Polar':
                        theta, r = vx, vy
                        theta = np.radians(theta)
                        vx = r * np.cos(theta)
                        vy = r * np.sin(theta)

                    vmax = np.nanmax(np.hypot(vx, vy))
                    diag = np.hypot(self.viewer.state.x_max-self.viewer.state.x_min,
                                      self.viewer.state.y_max-self.viewer.state.y_min)
                    scale = 0.05 * (layer_state.vector_scaling) * (diag / vmax) * (width / self.viewer.width())
                    xrange = abs(self.viewer.state.x_max-self.viewer.state.x_min)
                    yrange = abs(self.viewer.state.y_max-self.viewer.state.y_min)
                    minfrac = min(xrange / diag, yrange / diag)
                    arrow_scale = 0.2
                    angle = pi * minfrac / 3 if layer_state.vector_arrowhead else 0
                    vector_info = dict(scale=scale,
                                       angle=angle,
                                       name='quiver',
                                       arrow_scale=arrow_scale,
                                       line=dict(width=5),
                                       showlegend=False, hoverinfo='skip')
                    x_vec, y_vec = self._adjusted_vector_points(layer_state.vector_origin, scale, x, y, vx, vy)
                    if layer_state.cmap_mode == 'Fixed':
                        fig = ff.create_quiver(x_vec, y_vec, vx, vy, **vector_info)
                        fig.update_traces(marker=dict(color=layer_color))

                    else:
                        # start with the first quiver to add the rest
                        fig = ff.create_quiver([x[0]], [y[0]], [vx[0]], [vy[0]],
                                               **vector_info, line_color=marker['color'][0])
                        for i in range(1, len(marker['color'])):
                            fig1 = ff.create_quiver([x[i]], [y[i]], [vx[i]], [vy[i]],
                                                    **vector_info,
                                                    line_color=marker['color'][i])
                            fig.add_traces(data=fig1.data)
                    fig.update_layout(layout)

                # add line properties

                line = {}

                if layer_state.line_visible:
                    # convert linestyle names from glue values to plotly values
                    ls_dict = {'solid': 'solid', 'dotted': 'dot', 'dashed': 'dash', 'dashdot': 'dashdot'}
                    line['dash'] = ls_dict[layer_state.linestyle]
                    line['width'] = layer_state.linewidth

                    if layer_state.cmap_mode == 'Fixed':
                        marker['color'] = layer_color
                        mode = 'lines+markers'
                    else:
                        # set mode to markers and plot the colored line over it
                        mode = 'markers'
                        lc = plot_colored_line(self.viewer.axes, x, y, rgb_str)
                        segments = lc.get_segments()
                        # generate list of indices to parse colors over
                        indices = np.repeat(range(len(x)), 2)
                        indices = indices[1:len(x) * 2 - 1]
                        for i in range(len(segments)):
                            fig.add_trace(go.Scatter(
                                x=[segments[i][0][0], segments[i][1][0]],
                                y=[segments[i][0][1], segments[i][1][1]],
                                mode='lines',
                                line=dict(
                                    dash=ls_dict[layer_state.linestyle],
                                    width=layer_state.linewidth,
                                    color=rgb_str[indices[i]]),
                                showlegend=False,
                                hoverinfo='skip')
                            )
                else:
                    mode = 'markers'

                # add error bars

                xerr = {}
                if layer_state.xerr_visible:
                    xerr['type'] = 'data'
                    xerr['array'] = ensure_numerical(layer_state.layer[layer_state.xerr_att].ravel())
                    xerr['visible'] = True
                    # add points with error bars here if color mode is linear
                    if layer_state.cmap_mode == 'Linear':
                        for i, bar in enumerate(xerr['array']):
                            fig.add_trace(go.Scatter(
                                x=[x[i]],
                                y=[y[i]],
                                mode='markers',
                                error_x=dict(
                                    type='data', color=marker['color'][i],
                                    array=[bar], visible=True),
                                marker=dict(color=marker['color'][i]),
                                showlegend=False)
                            )

                yerr = {}
                if layer_state.yerr_visible:
                    yerr['type'] = 'data'
                    yerr['array'] = ensure_numerical(layer_state.layer[layer_state.yerr_att].ravel())
                    yerr['visible'] = True
                    # add points with error bars here if color mode is linear
                    if layer_state.cmap_mode == 'Linear':
                        for i, bar in enumerate(yerr['array']):
                            fig.add_trace(go.Scatter(
                                x=[x[i]],
                                y=[y[i]],
                                mode='markers',
                                error_y=dict(
                                    type='data', color=marker['color'][i],
                                    array=[bar], visible=True),
                                marker=dict(color=marker['color'][i]),
                                showlegend=False)
                            )

                # set log
                if self.viewer.state.x_log:
                    fig.update_xaxes(type='log', dtick=1, minor_ticks='outside',
                                     range=[np.log10(self.viewer.state.x_min),
                                            np.log10(self.viewer.state.x_max)]
                                     )
                if self.viewer.state.y_log:
                    fig.update_yaxes(type='log', dtick=1, minor_ticks='outside',
                                     range=[np.log10(self.viewer.state.y_min),
                                            np.log10(self.viewer.state.y_max)]
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

                # add layer to axesdict(
                scatter_info = dict(
                    mode=mode,
                    marker=marker,
                    line=line,
                    hoverinfo=hoverinfo,
                    hovertext=hovertext,
                    name=layer_state.layer.label
                )
                if polar:
                    scatter_info.update(theta=x, r=y, thetaunit=angle_unit)
                    fig.add_scatterpolar(**scatter_info)
                elif proj == 'rectilinear':
                    scatter_info.update(x=x, y=y)
                    # add error bars here if the color mode was fixed
                    if layer_state.cmap_mode == 'Fixed':
                        scatter_info.update(error_x=xerr, error_y=yerr)
                    fig.add_scatter(**scatter_info)
                else:
                    if not degrees:
                        x = x * 180 / np.pi
                        y = y * 180 / np.pi
                    fig.add_traces(data=go.Scattergeo(lon=x, lat=y))
                    fig.update_geos(projection_type=proj_type,
                                    showland=False, showcoastlines=False, showlakes=False,
                                    lataxis_showgrid=False, lonaxis_showgrid=False,
                                    bgcolor=settings.BACKGROUND_COLOR,
                                    framecolor=settings.FOREGROUND_COLOR)
                    fig.update_traces(**scatter_info)

            break

        plot(fig, filename=filename, auto_open=False)
