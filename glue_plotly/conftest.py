import numpy as np
import pytest

from glue.config import settings
from glue.core import Data

original_bg_color = None
original_fg_color = None

def pytest_addoption(parser):
    parser.addoption(
        "--fg-color",
        action="store",
        default="black",
        help="Foreground color for glue settings",
    )
    parser.addoption(
        "--bg-color",
        action="store",
        default="white",
        help="Background color for glue settings",
    )


def pytest_configure(config):
    global original_bg_color, original_fg_color

    from glue_plotly import setup
    setup()

    original_bg_color = settings.BACKGROUND_COLOR
    settings.BACKGROUND_COLOR = config.getoption("--bg-color")

    original_fg_color = settings.FOREGROUND_COLOR
    settings.FOREGROUND_COLOR = config.getoption("--fg-color")


def pytest_sessionfinish(session, exitstatus):
    settings.BACKGROUND_COLOR = original_bg_color
    settings.FOREGROUND_COLOR = original_fg_color


@pytest.fixture
def data_xyz():
    N = 100
    rng = np.random.default_rng(12345)
    x = rng.normal(10, 4, N)
    y = rng.normal(25, 10, N)
    return Data(label="Visual Scatter 2D", x=x, y=y)
