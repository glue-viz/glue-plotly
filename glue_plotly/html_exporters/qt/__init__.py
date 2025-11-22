from contextlib import suppress


def setup():

    from . import (
        histogram,  # noqa
        image,  # noqa
        profile,  # noqa
        scatter2d,  # noqa
        table,  # noqa
    )
    from .options_state import qt_export_options  # noqa

    # glue-qt plugins
    with suppress(ImportError):
        from . import dendrogram  # noqa

    # glue-vispy-viewers
    with suppress(ImportError):
        from . import scatter3d  # noqa
        from . import volume  # noqa
