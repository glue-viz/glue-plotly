import os

from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass

PLOTLY_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logo.png'))


def setup():

    from . import html_exporters  # noqa

    from glue.viewers.scatter.qt import ScatterViewer
    ScatterViewer.subtools['save'].append('save:plotly2d')

    try:
        from glue_vispy_viewers.scatter.scatter_viewer import VispyScatterViewer
    except ImportError:
        pass
    else:
        VispyScatterViewer.subtools['save'].append('save:plotly3d')
