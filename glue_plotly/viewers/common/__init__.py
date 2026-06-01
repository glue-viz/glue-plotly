from contextlib import suppress

with suppress(ImportError):
    from .tools import *  # noqa
