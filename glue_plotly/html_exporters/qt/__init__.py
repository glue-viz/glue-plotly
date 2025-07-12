from contextlib import suppress

from . import (
    histogram,  # noqa
    image,  # noqa
    profile,  # noqa
    scatter2d,  # noqa
    table,  # noqa
)
from .options_state import *  # noqa

# glue-qt plugins
with suppress(ImportError):
    from . import dendrogram  # noqa

# glue-vispy-viewers
with suppress(ImportError):
    from . import scatter3d  # noqa
    from . import volume  # noqa
