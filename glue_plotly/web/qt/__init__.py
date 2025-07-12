def setup():
    """The glue setup function for the Plotly Qt exporter."""
    from glue.config import exporters
    from glue_plotly.web.export_plotly import (
        DISPATCH,
        can_save_plotly,
        export_histogram,
        export_profile,
        export_scatter,
    )
    from glue_plotly.web.qt.exporter import save_plotly

    try:
        from glue_qt.plugins.dendro_viewer import DendrogramViewer

        from glue_plotly.web.export_plotly import export_dendrogram
        DISPATCH[DendrogramViewer] = export_dendrogram
    except ImportError:
        pass
    from glue_qt.viewers.histogram import HistogramViewer
    from glue_qt.viewers.profile import ProfileViewer
    from glue_qt.viewers.scatter import ScatterViewer

    DISPATCH[ScatterViewer] = export_scatter
    DISPATCH[HistogramViewer] = export_histogram
    DISPATCH[ProfileViewer] = export_profile

    exporters.add("Plotly", save_plotly, can_save_plotly)
