from glue.core import Data
from glue_qt.viewers.image.data_viewer import ImageViewer

from numpy import arange, ones

from .base import TestQtExporter


class TestImage(TestQtExporter):

    viewer_type = ImageViewer
    tool_id = 'save:plotlyimage'

    def make_data(self):
        return Data(label='d1', x=arange(24).reshape((2, 3, 4)), y=ones((2, 3, 4)))
