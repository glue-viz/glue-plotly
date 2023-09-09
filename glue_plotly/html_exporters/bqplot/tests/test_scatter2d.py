from glue.core import Data
from glue_jupyter.bqplot.scatter import BqplotScatterView

from .base import TestBqplotExporter


class TestScatter2D(TestBqplotExporter):

    viewer_type = BqplotScatterView
    tool_id = 'save:bqplot_plotly2d'

    def make_data(self):
        return Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label='d1')
