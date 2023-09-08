from glue.core import Data
from glue_qt.viewers.profile import ProfileViewer

from .base import TestQtExporter


class TestProfile(TestQtExporter):

    viewer_type = ProfileViewer
    tool_id = 'save:plotlyprofile'

    def make_data(self):
       return Data(x=[40, 41, 37, 63, 78, 35, 19, 100, 35, 86, 84, 99,
                      87, 56, 2, 71, 22, 36, 10, 1, 26, 70, 45, 20, 8],
                   label='d1')

    def setup_method(self, method):
        super().setup_method(method)
        self.viewer.state.x_att = self.data.id['Pixel Axis 0 [x]']
