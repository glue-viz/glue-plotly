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
    ScatterViewer.subtools['save'] = ScatterViewer.subtools['save'] + ['save:plotly2d']

    from glue.viewers.histogram.qt import HistogramViewer
    HistogramViewer.subtools['save'] = HistogramViewer.subtools['save'] + ['save:plotlyhist']

    try:
        from glue_vispy_viewers.scatter.scatter_viewer import VispyScatterViewer
    except ImportError:
        pass
    else:
        VispyScatterViewer.subtools['save'] = VispyScatterViewer.subtools['save'] + ['save:plotly3d']
