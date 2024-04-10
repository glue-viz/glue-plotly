from itertools import chain
from uuid import uuid4

from numpy import repeat

from glue_plotly.common import color_info
from glue_plotly.common.scatter2d import LINESTYLES, rectilinear_lines, scatter_mode, size_info
from glue.core import BaseData
from glue.utils import ensure_numerical
from glue.viewers.common.layer_artist import LayerArtist
from glue.viewers.scatter.state import ScatterLayerState

from plotly.graph_objs import Scatter, Scatterpolar


__all__ = ["PlotlyScatterLayerArtist"]


CMAP_PROPERTIES = {"cmap_mode", "cmap_att", "cmap_vmin", "cmap_vmax", "cmap"}
MARKER_PROPERTIES = {
    "size_mode",
    "size_att",
    "size_vmin",
    "size_vmax",
    "size_scaling",
    "size",
    "fill",
}
DENSITY_PROPERTIES = {"dpi", "stretch", "density_contrast"}
VISUAL_PROPERTIES = (
    CMAP_PROPERTIES
    | MARKER_PROPERTIES
    | DENSITY_PROPERTIES
    | {"color", "alpha", "zorder", "visible"}
)

LIMIT_PROPERTIES = {"x_min", "x_max", "y_min", "y_max"}
DATA_PROPERTIES = {
    "layer",
    "x_att",
    "y_att",
    "cmap_mode",
    "size_mode",
    "density_map",
    "vector_visible",
    "vx_att",
    "vy_att",
    "vector_arrowhead",
    "vector_mode",
    "vector_origin",
    "line_visible",
    "markers_visible",
    "vector_scaling",
}
LINE_PROPERTIES = {"line_visible", "cmap_mode", "linestyle", "linewidth", "color"}


class PlotlyScatterLayerArtist(LayerArtist):

    _layer_state_cls = ScatterLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super().__init__(
            viewer_state,
            layer_state=layer_state,
            layer=layer
        )

        self._viewer_state.add_global_callback(self._update_display)
        self.state.add_global_callback(self._update_display)

        self.view = view

        # Somewhat annoyingly, the trace that we pass in to be added
        # is NOT the same instance that ends up living in the figure.
        # (see basedatatypes.py line 2251 in the Plotly package)
        # So we abuse the metadata entry of the trace to tag it with
        # a UUID so that we can extract it when needed.
        # Note that setting the UID directly (either in the Scatter
        # constructor or after) doesn't seem to work - it gets
        # overridden by Plotly
        self._scatter_id = uuid4().hex
        scatter = self._create_scatter()
        self.view.figure.add_trace(scatter)

        self._lines_id = None
        self._error_id = None
        self._vector_id = None

    def remove(self):
        self.view._remove_traces([self._get_scatter()])
        self.view._remove_traces(self._get_lines())
        self.view._remove_traces(self._get_error_bars())
        self.view._remove_traces(self._get_vectors())
        return super().remove()

    def _get_traces_with_id(self, id):
        return self.view.figure.select_traces(dict(meta=id))

    def _get_scatter(self):
        return next(self._get_traces_with_id(self._scatter_id))

    def _get_lines(self):
        return self._get_traces_with_id(self._lines_id)

    def _get_error_bars(self):
        return self._get_traces_with_id(self._error_id)

    def _get_vectors(self):
        return self._get_traces_with_id(self._vector_id)

    def traces(self):
        return chain([self._get_scatter()], self._get_lines(), self._get_error_bars(), self._get_vectors())

    def _update_data(self):

        x = ensure_numerical(self.layer[self._viewer_state.x_att].ravel())
        y = ensure_numerical(self.layer[self._viewer_state.y_att].ravel())

        scatter = self._get_scatter()
        if self._viewer_state.using_rectilinear:
            scatter.update(x=x, y=y)
        else:
            scatter.update(theta=x, r=y)

    def _create_scatter(self):
        if isinstance(self.layer, BaseData):
            name = self.layer.label
        else:
            name = f"{self.layer.label} ({self.layer.data.label})"

        scatter_info = dict(mode=scatter_mode(self.state),
                            name=name,
                            hoverinfo='all',
                            unselected=dict(marker=dict(opacity=self.state.alpha)),
                            meta=self._scatter_id)
        if self._viewer_state.using_rectilinear:
            scatter = Scatter(**scatter_info)
        else:
            theta_unit = 'degrees' if self.view.state.using_degrees else 'radians'
            scatter_info.update(thetaunit=theta_unit)
            scatter = Scatterpolar(**scatter_info)
        return scatter

    def _update_display(self, force=False, **kwargs):
        changed = self.pop_changed_properties()

        if 'layout_update' in kwargs:
            self.view._clear_traces()
            scatter = self._create_scatter()
            self.view.figure.add_trace(scatter)
            force = True

        if force or len(changed & DATA_PROPERTIES) > 0:
            self._update_data()
            force = True

        if force or len(changed & VISUAL_PROPERTIES) > 0:
            self._update_visual_attributes(changed, force=force)

        if force or len(changed & LINE_PROPERTIES) > 0:
            self._update_lines(changed, force=force)

        if force or "zorder" in changed:
            self._update_zorder()

    def _update_zorder(self):
        traces = [self.view.selection_layer]
        for layer in self.view.layers:
            traces += list(layer.traces())
        self.view.figure.data = traces

    def _update_lines(self, changed, force=False):
        scatter = self._get_scatter()
        fixed_color = self.state.cmap_mode == 'Fixed'
        lines = list(self._get_lines())

        with self.view.figure.batch_update():
            scatter.update(mode=scatter_mode(self.state))

            line_traces_visible = True
            if force or "cmap_mode" in changed:
                if not (fixed_color or lines):
                    line, lines = rectilinear_lines(self.state, scatter.marker, scatter.x, scatter.y)
                    if lines:
                        self._lines_id = lines[0].meta
                    self.view.figure.add_traces(lines)

                    # The newly-created line traces already have the correct properties, so we can return
                    return

                elif fixed_color and lines:
                    line_traces_visible = False

            if (force or "line_visible" in changed) or not line_traces_visible:
                visible = False if not line_traces_visible else self.state.line_visible
                self.view.figure.for_each_trace(lambda t: t.update(visible=visible), dict(meta=self._lines_id))

            if force or len(changed & {"linestyle", "linewidth", "color"}) > 0:
                linestyle = LINESTYLES[self.state.linestyle]
                if fixed_color:
                    line = scatter.line.update(dash=linestyle, width=self.state.linewidth)
                    scatter.update(line=line)
                else:
                    rgba_strs = scatter.marker.color
                    count = len(scatter.x)
                    indices = repeat(range(count), 2)
                    indices = indices[1:count * 2 - 1]
                    for i, line in enumerate(lines):
                        line_data = line.line
                        line_data.update(dash=linestyle, width=self.state.linewidth, color=rgba_strs[indices[i]])
                        line.update(line=line_data)

    def _update_visual_attributes(self, changed, force=False):

        if not self.enabled:
            return

        # Only run select_traces once
        scatter = self._get_scatter()

        if self.state.markers_visible:
            if force or \
                    any(prop in changed for prop in CMAP_PROPERTIES) or \
                    any(prop in changed for prop in ["color", "fill"]):

                color = color_info(self.state)
                if self.state.fill:
                    scatter.marker.update(color=color,
                                          line=dict(width=0),
                                          opacity=self.state.alpha)
                else:
                    scatter.marker.update(color='rgba(0, 0, 0, 0)',
                                          opacity=self.state.alpha,
                                          line=dict(width=1,
                                                    color=color)
                                          )

            if force or any(prop in changed for prop in MARKER_PROPERTIES):
                scatter.marker['size'] = size_info(self.state)

        if force or "alpha" in changed:
            marker = scatter.marker
            opacity_dict = dict(opacity=self.state.alpha)
            marker.update(**opacity_dict)
            scatter.update(marker=marker,
                           unselected=dict(marker=opacity_dict))

        if force or "visible" in changed:
            scatter.visible = self.state.visible

    def update(self, **kwargs):
        self._update_display(force=True, **kwargs)
