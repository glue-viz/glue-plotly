from glue_jupyter.common.state_widgets.viewer_histogram import HistogramViewerStateWidget


class PlotlyHistogramViewerStateWidget(HistogramViewerStateWidget):

    template_file = (__file__, "viewer_state_widget.vue")
