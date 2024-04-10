from glue.core.subset import XRangeROI, roi_to_subset_state
from glue.viewers.histogram.state import HistogramViewerState
from glue_plotly.common import base_layout_config, base_rectilinear_axis
from glue_plotly.viewers import PlotlyBaseView
from glue_plotly.viewers.histogram.layer_artist import PlotlyHistogramLayerArtist

from glue_jupyter.registries import viewer_registry
from glue_jupyter.common.state_widgets.layer_histogram import HistogramLayerStateWidget
from glue_jupyter.common.state_widgets.viewer_histogram import HistogramViewerStateWidget


__all__ = ["PlotlyHistogramView"]


@viewer_registry("plotly_histogram")
class PlotlyHistogramView(PlotlyBaseView):

    tools = ['plotly:home', 'plotly:zoom', 'plotly:pan', 'plotly:xrange', 'plotly:hover']

    allow_duplicate_data = False
    allow_duplicate_subset = False

    _state_cls = HistogramViewerState
    _options_cls = HistogramViewerStateWidget
    _data_artist_cls = PlotlyHistogramLayerArtist
    _subset_artist_cls = PlotlyHistogramLayerArtist
    _layer_style_widget_cls = HistogramLayerStateWidget

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state.add_callback('x_att', self._update_axes)
        self.state.add_callback('normalize', self._update_axes)
        self._update_axes()

    def _create_layout_config(self):
        config = base_layout_config(self, barmode="overlay", bargap=0,
                                    width=1000, height=600,
                                    **self.LAYOUT_SETTINGS)
        x_axis = base_rectilinear_axis(self.state, 'x')
        x_axis.update(showline=False)
        y_axis = base_rectilinear_axis(self.state, 'y')
        y_axis.update(showline=False)
        config.update(xaxis=x_axis, yaxis=y_axis)
        return config

    def _update_axes(self, *args):
        if self.state.x_att is not None:
            self.state.x_axislabel = str(self.state.x_att)

        if self.state.normalize:
            self.state.y_axislabel = 'Normalized number'
        else:
            self.state.y_axislabel = 'Number'

    def _roi_to_subset_state(self, roi):
        return roi_to_subset_state(roi, x_att=self.state.x_att)

    def apply_roi(self, roi, override_mode=False):
        if len(self.layers) == 0:
            return

        bins = self.state.bins

        x = roi.to_polygon()[0]
        lo, hi = min(x), max(x)

        if lo >= bins.min():
            lo = bins[bins <= lo].max()
        if hi <= bins.max():
            hi = bins[bins >= hi].min()

        roi_new = XRangeROI(min=lo, max=hi)
        subset_state = roi_to_subset_state(roi_new, x_att=self.state.x_att, x_categories=self.state.x_categories)
        self.apply_subset_state(subset_state, override_mode=override_mode)
