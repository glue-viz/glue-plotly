import numpy as np
import pytest

from glue.core import Data


def pytest_configure(config):
    from glue_plotly import setup
    setup()


@pytest.fixture
def data_xyz():
    N = 100
    rng = np.random.default_rng(12345)
    x = rng.normal(10, 4, N)
    y = rng.normal(25, 10, N)
    return Data(label="Visual Scatter 2D", x=x, y=y)
