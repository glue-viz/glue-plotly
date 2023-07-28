from uuid import uuid4

from glue_plotly.common import color_info
from glue_plotly.common.scatter2d import size_info
from glue.utils import ensure_numerical
from glue.viewers.common.layer_artist import LayerArtist
from glue.viewers.scatter.state import ScatterLayerState

from plotly.graph_objs import Scatter


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

class PlotlyScatterLayerArtist(LayerArtist):

    _layer_state_cls = ScatterLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super().__init__(
            viewer_state,
            layer_state=layer_state,
            layer=layer
        )

        self._viewer_state.add_global_callback(self._update_scatter)
        self.state.add_global_callback(self._update_scatter)

        self.view = view

        # Somewhat annoyingly, the trace that we pass in to be added
        # is NOT the same instance that ends up living in the figure.
        # (see basedatatypes.py line 2251 in the Plotly package)
        # So we abuse the metadata entry of the trace to tag it with
        # a UUID so that we can extract it when needed.
        # Note that setting the UID directly (either in the Scatter
        # constructor or after) doesn't seem to work - it gets
        # overridden by Plotly
        self.scatter_id = uuid4().hex
        scatter = Scatter(x=[0, 1], y=[0, 1],
                          mode="markers",
                          meta=self.scatter_id)
        self.view.figure.add_trace(scatter)

    def _get_scatter(self):
        return next(self.view.figure.select_traces(dict(meta=self.scatter_id)))

    def _update_data(self):

        x = ensure_numerical(self.layer[self._viewer_state.x_att].ravel())
        y = ensure_numerical(self.layer[self._viewer_state.y_att].ravel())

        scatter = self._get_scatter()
        scatter.update(x=x, y=y)

    def _update_scatter(self, force=False, **kwargs):

        changed = self.pop_changed_properties()
        
        if force or len(changed & DATA_PROPERTIES) > 0:
            self._update_data()
            force = True

        if force or len(changed & VISUAL_PROPERTIES) > 0:
            self._update_visual_attributes(changed, force=force)

    def _update_visual_attributes(self, changed, force=False):

        if not self.enabled:
            return

        # Only run select_traces once
        scatter = self._get_scatter()

        if self.state.markers_visible:
            if force or \
                any(prop in changed for prop in CMAP_PROPERTIES) or \
                any(prop in changed for prop in ["color", "fill"]):
                    
                color = color_info(self)
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
                scatter.marker['size'] = size_info(self)

        if force or "alpha" in changed:
            scatter.marker['opacity'] = self.state.alpha

        if force or "visible" in changed:
            scatter.visible = self.state.visible

    def update(self):
        self._update_scatter()
        
        
