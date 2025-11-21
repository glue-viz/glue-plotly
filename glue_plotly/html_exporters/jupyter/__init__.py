from contextlib import suppress


def setup():

    with suppress(ImportError):
        from . import histogram  # noqa
        from . import image  # noqa
        from . import profile  # noqa
        from . import scatter2d  # noqa
        
        # glue-vispy-viewers
        try:
            from . import scatter3d  # noqa
            from . import volume  # noqa
        except ImportError:
            pass
