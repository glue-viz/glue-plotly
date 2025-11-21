import importlib.metadata
import os
from contextlib import suppress

__version__ = importlib.metadata.version("glue-plotly")


PLOTLY_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), "logo"))
PLOTLY_ERROR_MESSAGE = "An error occurred during the export to Plotly:"


def setup():
    with suppress(ImportError):
        setup_qt()

    with suppress(ImportError):
        setup_jupyter()


def setup_qt():
    """Performs necessary setup for using glue-plotly with glue-qt."""
    from . import common  # noqa
    from .html_exporters.qt import setup as exporters_setup # noqa
    from .web.qt import setup as web_setup
    exporters_setup()
    web_setup()

    from glue_qt.viewers.scatter import ScatterViewer
    ScatterViewer.subtools = {
        **ScatterViewer.subtools,
        "save": ScatterViewer.subtools["save"] + ["save:plotly2d"]
    }

    from glue_qt.viewers.image import ImageViewer
    ImageViewer.subtools = {
        **ImageViewer.subtools,
        "save": ImageViewer.subtools["save"] + ["save:plotlyimage2d"]
    }

    from glue_qt.viewers.histogram import HistogramViewer
    HistogramViewer.subtools = {
        **HistogramViewer.subtools,
        "save": HistogramViewer.subtools["save"] + ["save:plotlyhist"]
    }

    from glue_qt.viewers.profile import ProfileViewer
    ProfileViewer.subtools = {
        **ProfileViewer.subtools,
        "save": ProfileViewer.subtools["save"] + ["save:plotlyprofile"]
    }

    from glue_qt.viewers.table import TableViewer
    TableViewer.tools += ["save:plotlytable"]

    try:
        from glue_qt.plugins.dendro_viewer import DendrogramViewer
    except ImportError:
        pass
    else:
        DendrogramViewer.subtools = {
            **DendrogramViewer.subtools,
            "save": DendrogramViewer.subtools["save"] + ["save:plotlydendro"]
        }

    try:
        from glue_vispy_viewers.scatter.qt.scatter_viewer import VispyScatterViewer
        from glue_vispy_viewers.volume.qt.volume_viewer import VispyVolumeViewer
    except ImportError:
        pass
    else:
        VispyScatterViewer.subtools = {
            **VispyScatterViewer.subtools,
            "save": VispyScatterViewer.subtools["save"] + ["save:plotly3d"]
        }
        VispyVolumeViewer.subtools = {
            **VispyVolumeViewer.subtools,
            "save": VispyVolumeViewer.subtools["save"] + ["save:plotlyvolume"]
        }


def setup_jupyter():
    """Performs necessary setup for using glue-plotly with glue-jupyter."""
    from .html_exporters.jupyter import setup as exporters_setup
    from glue_jupyter.bqplot.histogram import BqplotHistogramView
    from glue_jupyter.bqplot.image import BqplotImageView
    from glue_jupyter.bqplot.profile import BqplotProfileView
    from glue_jupyter.bqplot.scatter import BqplotScatterView
    from glue_jupyter.ipyvolume import IpyvolumeScatterView, IpyvolumeVolumeView
    exporters_setup()

    BqplotHistogramView.tools += ["save:bqplot_plotlyhist"]
    BqplotImageView.tools += ["save:bqplot_plotlyimage2d"]
    BqplotProfileView.tools += ["save:bqplot_plotlyprofile"]
    BqplotScatterView.tools += ["save:bqplot_plotly2d"]
    IpyvolumeScatterView.tools = list(IpyvolumeScatterView.tools) + \
                                 ["save:jupyter_plotly3dscatter"]
    IpyvolumeVolumeView.tools = list(IpyvolumeVolumeView.tools) + \
                                ["save:jupyter_plotlyvolume"]

    try:
        from glue_vispy_viewers.scatter.jupyter import JupyterVispyScatterViewer
        from glue_vispy_viewers.volume.jupyter import JupyterVispyVolumeViewer
    except ImportError:
        pass
    else:
        JupyterVispyScatterViewer.tools += ["save:jupyter_plotly3dscatter"]
        JupyterVispyVolumeViewer.tools += ["save:jupyter_plotlyvolume"]

    from .viewers.common import tools  # noqa
