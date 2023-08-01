from glue.viewers.histogram.state import HistogramViewerState
from glue_plotly.viewers import PlotlyBaseView
from glue_plotly.viewers.histogram.layer_artist import PlotlyHistogramLayerArtist


try:
    from glue_jupyter.registries import viewer_registry
    from glue_jupyter.common.state_widgets.layer_histogram import HistogramLayerStateWidget
    from glue_jupyter.common.state_widgets.viewer_histogram import HistogramViewerStateWidget
except ImportError:
    HistogramLayerStateWidget = None
    HistogramViewerStateWidget = None
    viewer_registry = None


@viewer_registry("plotly_histogram")
class PlotlyHistogramView(PlotlyBaseView):

    tools = ['plotly:home', 'plotly:zoom', 'plotly:pan', 'plotly:xrange']

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
        self._update_axes()

    def _update_axes(self, *args):
        if self.state.x_att is not None:
            self.state.x_axislabel = str(self.state.x_att)
        
