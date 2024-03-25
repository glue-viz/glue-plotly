from glue_jupyter import jglue

from glue_plotly.viewers.common.tests.utils import ExampleViewer


class TestTools(object):

    def setup_method(self, method):
        self.app = jglue()
        self.viewer = self.app.new_data_viewer(ExampleViewer)

    def teardown_method(self, method):
        pass

    def get_tool(self, id):
        return self.viewer.toolbar.tools[id]

    def test_rectzoom(self):
        tool = self.get_tool('plotly:zoom')
        tool.activate()
        assert self.viewer.figure.layout['selectdirection'] == 'any'
        assert self.viewer.figure.layout['dragmode'] == 'select'
        tool.deactivate()
        assert self.viewer.figure.layout['dragmode'] is False

    def test_hzoom(self):
        tool = self.get_tool('plotly:hzoom')
        tool.activate()
        assert self.viewer.figure.layout['selectdirection'] == 'h'
        assert self.viewer.figure.layout['dragmode'] == 'select'
        tool.deactivate()
        assert self.viewer.figure.layout['dragmode'] is False

    def test_vzoom(self):
        tool = self.get_tool('plotly:vzoom')
        tool.activate()
        assert self.viewer.figure.layout['selectdirection'] == 'v'
        assert self.viewer.figure.layout['dragmode'] == 'select'
        tool.deactivate()
        assert self.viewer.figure.layout['dragmode'] is False

    def test_pan(self):
        tool = self.get_tool('plotly:pan')
        tool.activate()
        assert self.viewer.figure.layout['dragmode'] == 'pan'
        tool.deactivate()
        assert self.viewer.figure.layout['dragmode'] is False

    def test_hrange_select(self):
        tool = self.get_tool('plotly:xrange')
        tool.activate()
        assert self.viewer.figure.layout['selectdirection'] == 'h'
        assert self.viewer.figure.layout['dragmode'] == 'select'
        tool.deactivate()
        assert self.viewer.figure.layout['dragmode'] is False

    def test_vrange_select(self):
        tool = self.get_tool('plotly:yrange')
        tool.activate()
        assert self.viewer.figure.layout['selectdirection'] == 'v'
        assert self.viewer.figure.layout['dragmode'] == 'select'
        tool.deactivate()
        assert self.viewer.figure.layout['dragmode'] is False

    def test_rect_select(self):
        tool = self.get_tool('plotly:rectangle')
        tool.activate()
        assert self.viewer.figure.layout['selectdirection'] == 'any'
        assert self.viewer.figure.layout['dragmode'] == 'select'
        tool.deactivate()
        assert self.viewer.figure.layout['dragmode'] is False

    def test_lasso_select(self):
        tool = self.get_tool('plotly:lasso')
        tool.activate()
        assert self.viewer.figure.layout['dragmode'] == 'lasso'
        tool.deactivate()
        assert self.viewer.figure.layout['dragmode'] is False

    def test_home(self):
        xmin, xmax = self.viewer.state.x_min, self.viewer.state.x_max
        ymin, ymax = self.viewer.state.y_min, self.viewer.state.y_max
        self.viewer.state.x_min = 10
        self.viewer.state.x_max = 27
        self.viewer.state.y_min = -5
        self.viewer.state.y_max = 13
        tool = self.get_tool('plotly:home')
        tool.activate()
        print(self.viewer.state)
        assert self.viewer.state.x_min == xmin
        assert self.viewer.state.x_max == xmax
        assert self.viewer.state.y_min == ymin
        assert self.viewer.state.y_max == ymax
        xaxis = self.viewer.figure.layout.xaxis
        assert xaxis.range == (xmin, xmax)
        yaxis = self.viewer.figure.layout.yaxis
        assert yaxis.range == (ymin, ymax)

    def test_hover(self):
        tool = self.get_tool('plotly:hover')
        tool.activate()
        assert self.viewer.figure.layout['hovermode'] == 'closest'
        tool.deactivate()
        assert self.viewer.figure.layout['hovermode'] is False
