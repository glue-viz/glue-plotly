from glue.viewers.scatter.state import ScatterViewerState
from glue_jupyter.common.state_widgets.viewer_scatter import ScatterViewerStateWidget
from glue_jupyter.common.state_widgets.layer_scatter import ScatterLayerStateWidget
from glue_jupyter.registries import viewer_registry

from .layer_artist import PlotlyScatterLayerArtist
from glue_plotly.viewers import PlotlyBaseView

@viewer_registry("plotly_scatter")
class PlotlyScatterView(PlotlyBaseView):

    tools = ['plotly:home', 'plotly:zoom', 'plotly:pan', 'plotly:xrange',
             'plotly:yrange', 'plotly:rectangle', 'plotly:lasso']

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
        self._update_axes()

    def _update_axes(self, *args):

        if self.state.x_att is not None:
            self.state.x_axislabel = str(self.state.x_att)

        if self.state.y_att is not None:
            self.state.y_axislabel = str(self.state.y_att)
