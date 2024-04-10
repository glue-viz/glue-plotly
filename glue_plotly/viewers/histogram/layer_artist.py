import numpy as np

from glue.core.exceptions import IncompatibleAttribute
from glue.viewers.common.layer_artist import LayerArtist
from glue.viewers.histogram.state import HistogramLayerState
from glue_plotly.common.common import fixed_color

from glue_plotly.common.histogram import traces_for_layer

__all__ = ["PlotlyHistogramLayerArtist"]

SCALE_PROPERTIES = {'y_log', 'normalize', 'cumulative'}
HISTOGRAM_PROPERTIES = SCALE_PROPERTIES | {'layer', 'x_att', 'hist_x_min',
                                           'hist_x_max', 'hist_n_bin', 'x_log'}
VISUAL_PROPERTIES = {'alpha', 'color', 'zorder', 'visible'}
DATA_PROPERTIES = {'layer', 'x_att', 'y_att'}


class PlotlyHistogramLayerArtist(LayerArtist):

    _layer_state_cls = HistogramLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):

        super().__init__(
            viewer_state,
            layer_state=layer_state,
            layer=layer
        )

        self.view = view
        self.bins = None
        self._bars_id = None

        self._viewer_state.add_global_callback(self._update_histogram)
        self.state.add_global_callback(self._update_histogram)

    def _get_bars(self):
        return self.view.figure.select_traces(dict(meta=self._bars_id))

    def traces(self):
        return self._get_bars()

    def _calculate_histogram(self):
        try:
            self.state.reset_cache()
            self.bins, self.hist_unscaled = self.state.histogram
        except IncompatibleAttribute:
            self.disable('Could not compute histogram')
            self.bins = self.hist_unscaled = None

    def _scale_histogram(self):

        if self.bins is None:
            return  # can happen when the subset is empty

        if self.bins.size == 0:
            return

        with self.view.figure.batch_update():

            # We have to do the following to make sure that we reset the y_max as
            # needed. We can't simply reset based on the maximum for this layer
            # because other layers might have other values, and we also can't do:
            #
            #   self._viewer_state.y_max = max(self._viewer_state.y_max, result[0].max())
            #
            # because this would never allow y_max to get smaller.

            _, hist = self.state.histogram
            self.state._y_max = hist.max()
            if self._viewer_state.y_log:
                self.state._y_max *= 2
            else:
                self.state._y_max *= 1.2

            if self._viewer_state.y_log:
                keep = hist > 0
                if np.any(keep):
                    self.state._y_min = hist[keep].min() / 10
                else:
                    self.state._y_min = 0
            else:
                self.state._y_min = 0

            largest_y_max = max(getattr(layer, '_y_max', 0)
                                for layer in self._viewer_state.layers)
            if np.isfinite(largest_y_max) and largest_y_max != self._viewer_state.y_max:
                self._viewer_state.y_max = largest_y_max

            smallest_y_min = min(getattr(layer, '_y_min', np.inf)
                                 for layer in self._viewer_state.layers)
            if np.isfinite(smallest_y_min) and smallest_y_min != self._viewer_state.y_min:
                self._viewer_state.y_min = smallest_y_min

    def _update_visual_attributes(self, changed, force=False):
        if not self.enabled:
            return

        with self.view.figure.batch_update():
            self.view.figure.for_each_trace(self._update_visual_attrs_for_trace, dict(meta=self._bars_id))

    def _update_visual_attrs_for_trace(self, trace):
        marker = trace.marker
        marker.update(opacity=self.state.alpha, color=fixed_color(self.state))
        trace.update(marker=marker,
                     visible=self.state.visible,
                     unselected=dict(marker=dict(opacity=self.state.alpha)))

    def _update_data(self):
        old_bars = self._get_bars()
        if old_bars:
            with self.view.figure.batch_update():
                for bar in old_bars:
                    self.view._remove_trace_index(bar)
            # self.view._remove_traces(old_bars)

        bars = traces_for_layer(self.view.state, self.state, add_data_label=True)
        for bar in bars:
            bar.update(hoverinfo='all', unselected=dict(marker=dict(opacity=self.state.alpha)))
        self._bars_id = bars[0].meta if bars else None
        self.view.figure.add_traces(bars)

    def _update_zorder(self):
        traces = [self.view.selection_layer]
        for layer in self.view.layers:
            traces += list(layer.traces())
        self.view.figure.data = traces

    def _update_histogram(self, force=False, **kwargs):
        if (self._viewer_state.hist_x_min is None or
                self._viewer_state.hist_x_max is None or
                self._viewer_state.hist_n_bin is None or
                self._viewer_state.x_att is None or
                self.state.layer is None):
            return

        changed = self.pop_changed_properties()

        if force or len(changed & HISTOGRAM_PROPERTIES) > 0:
            self._calculate_histogram()
            force = True

        if force or len(changed & DATA_PROPERTIES) > 0:
            self._update_data()
            force = True

        if force or len(changed & SCALE_PROPERTIES) > 0:
            self._scale_histogram()

        if force or len(changed & VISUAL_PROPERTIES) > 0:
            self._update_visual_attributes(changed, force=force)

        if force or "zorder" in changed:
            self._update_zorder()

    def update(self):
        self.state.reset_cache()
        self._update_histogram(force=True)
