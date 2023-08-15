def setup():

    from glue.config import exporters
    from glue_plotly.web.export_plotly import (can_save_plotly, DISPATCH,
                                               export_scatter, export_histogram,
                                               export_profile)
    from glue_plotly.web.qt.exporter import save_plotly

    from glue_qt.viewers.scatter import ScatterViewer
    from glue_qt.viewers.histogram import HistogramViewer
    from glue_qt.viewers.profile import ProfileViewer

    DISPATCH[ScatterViewer] = export_scatter
    DISPATCH[HistogramViewer] = export_histogram
    DISPATCH[ProfileViewer] = export_profile

    exporters.add('Plotly', save_plotly, can_save_plotly)
