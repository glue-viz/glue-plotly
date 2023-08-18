import os

from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass

PLOTLY_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logo.png'))
PLOTLY_ERROR_MESSAGE = "An error occurred during the export to Plotly:"


def setup():

    from . import common  # noqa
    from . import html_exporters  # noqa
    from .web.qt import setup
    setup()

    from glue_qt.viewers.scatter import ScatterViewer
    ScatterViewer.subtools = {
        **ScatterViewer.subtools,
        "save": ScatterViewer.subtools["save"] + ['save:plotly2d']
    }

    from glue_qt.viewers.image import ImageViewer
    ImageViewer.subtools = {
        **ImageViewer.subtools,
        "save": ImageViewer.subtools["save"] + ['save:plotlyimage2d']
    }

    from glue_qt.viewers.histogram import HistogramViewer
    HistogramViewer.subtools = {
        **HistogramViewer.subtools,
        "save": HistogramViewer.subtools["save"] + ['save:plotlyhist']
    }

    from glue_qt.viewers.profile import ProfileViewer
    ProfileViewer.subtools = {
        **ProfileViewer.subtools,
        "save": ProfileViewer.subtools["save"] + ['save:plotlyprofile']
    }

    from glue_qt.viewers.table import TableViewer
    TableViewer.tools += ['save:plotlytable']

    try:
        from glue_qt.plugins.dendro_viewer import DendrogramViewer
    except ImportError:
        pass
    else:
        DendrogramViewer.subtools = {
            **DendrogramViewer.subtools,
            "save": DendrogramViewer.subtools["save"] + ['save:plotlydendro']
        }

    try:
        from glue_vispy_viewers.scatter.scatter_viewer import VispyScatterViewer
    except ImportError:
        pass
    else:
        VispyScatterViewer.subtools['save'] = VispyScatterViewer.subtools['save'] + ['save:plotly3d']
