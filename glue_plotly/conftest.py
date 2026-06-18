import numpy as np
import pytest

from glue.core import Data


def pytest_configure(config):
    from glue_plotly import setup
    setup()


@pytest.fixture
def data_xyz():
    N = 100
    np.random.seed(12345)
    x = np.random.normal(10, 4, N)
    y = np.random.normal(25, 10, N)
    return Data(label="Visual Scatter 2D", x=x, y=y)
