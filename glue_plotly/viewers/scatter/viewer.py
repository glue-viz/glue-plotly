from plotly.graph_objs import Layout

from glue.core.subset import roi_to_subset_state
from glue.viewers.scatter.state import ScatterViewerState

from glue_plotly.common.scatter2d import polar_layout_config, radial_axis, rectilinear_layout_config

from glue_jupyter.common.state_widgets.viewer_scatter import ScatterViewerStateWidget
from glue_jupyter.common.state_widgets.layer_scatter import ScatterLayerStateWidget
from glue_jupyter.registries import viewer_registry

from .layer_artist import PlotlyScatterLayerArtist
from glue_plotly.viewers import PlotlyBaseView


__all__ = ["PlotlyScatterView"]


@viewer_registry("plotly_scatter")
class PlotlyScatterView(PlotlyBaseView):

    tools = ['plotly:home', 'plotly:zoom', 'plotly:pan', 'plotly:xrange',
             'plotly:yrange', 'plotly:rectangle', 'plotly:lasso', 'plotly:hover']

    allow_duplicate_data = False
    allow_duplicate_subset = False
    large_data_size = 1e7

    _state_cls = ScatterViewerState
    _options_cls = ScatterViewerStateWidget
    _data_artist_cls = PlotlyScatterLayerArtist
    _subset_artist_cls = PlotlyScatterLayerArtist
    _layer_style_widget_cls = ScatterLayerStateWidget

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state.add_callback('x_att', self._update_axes)
        self.state.add_callback('y_att', self._update_axes)
        self.state.add_callback('plot_mode', self._update_projection)

        self._update_axes()

    def _create_layout_config(self):
        if self.state.using_rectilinear:
            config = rectilinear_layout_config(self, **self.LAYOUT_SETTINGS)
            config['xaxis']['showline'] = False
            config['yaxis']['showline'] = False
            return config
        else:  # For now, that means polar
            return polar_layout_config(self, radial_axis, **self.LAYOUT_SETTINGS)

    def _update_projection(self, *args):
        config = self._create_layout_config()
        traces = self.figure.data
        layout = Layout(**config)
        self.figure.update(layout=layout)

        # For some reason doing these updates in the layout config
        # doesn't seem to get rid of pre-existing axes
        if self.state.using_rectilinear:
            self.figure.update_layout(polar=None, xaxis=dict(visible=True), yaxis=dict(visible=True))
        else:
            self.figure.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False))
        self.figure.data = traces
        for layer in self.layers:
            layer.update(layout_update=True)
        self.figure.update()

    def _update_axes(self, *args):
        if self.state.x_att is not None:
            self.state.x_axislabel = str(self.state.x_att)

        if self.state.y_att is not None:
            self.state.y_axislabel = str(self.state.y_att)

    def _roi_to_subset_state(self, roi):
        return roi_to_subset_state(roi, x_att=self.state.x_att, y_att=self.state.y_att)
