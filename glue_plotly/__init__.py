import os

PLOTLY_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logo.png'))


def setup():
    from glue.viewers.scatter.qt import ScatterViewer
    from . import html_exporters  # noqa
    ScatterViewer.subtools['save'].append('save:plotly')
    from .web.qt import setup
    setup()
