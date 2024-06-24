from glue.viewers.histogram.state import DDCProperty, HistogramViewerState


__all__ = ["PlotlyHistogramViewerState"]


class PlotlyHistogramViewerState(HistogramViewerState):

    gaps = DDCProperty(False, docstring='Whether to include gaps between histogram bars')
    gap_fraction = DDCProperty(0.15,
                               docstring='The gap fraction if using gaps. For example, '
                                         '0 means that no gap between bars, 0.5 means '
                                         'that the bars and gaps are evenly sized, and 1 '
                                         'means that the entire bar mark is gap.')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
