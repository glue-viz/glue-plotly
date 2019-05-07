import os

PLOTLY_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logo.png'))


def setup():
    from glue.viewers.scatter.qt import ScatterViewer
    from glue_vispy_viewers.scatter.scatter_viewer import VispyScatterViewer
    from . import html_exporters  # noqa
    ScatterViewer.subtools['save'].append('save:plotly2d')
    VispyScatterViewer.subtools['save'].append('save:plotly3d')

