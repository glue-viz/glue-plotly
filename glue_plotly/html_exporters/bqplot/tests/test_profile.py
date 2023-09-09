from glue.core import Data
from glue_jupyter.bqplot.profile import BqplotProfileView

from .base import TestBqplotExporter


class TestProfile(TestBqplotExporter):

    viewer_type = BqplotProfileView
    tool_id = 'save:bqplot_plotlyprofile'

    def make_data(self):
        return Data(x=[40, 41, 37, 63, 78, 35, 19, 100, 35, 86, 84, 99,
                       87, 56, 2, 71, 22, 36, 10, 1, 26, 70, 45, 20, 8],
                    label='d1')
