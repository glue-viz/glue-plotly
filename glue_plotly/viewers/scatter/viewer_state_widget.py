from glue_jupyter.common.state_widgets.viewer_scatter import ScatterViewerStateWidget


class PlotlyScatterViewerStateWidget(ScatterViewerStateWidget):

    template_file = (__file__, "viewer_state_widget.vue")
