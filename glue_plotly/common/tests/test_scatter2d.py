from itertools import product
from glue.core.link_helpers import LinkSame

from matplotlib import colormaps
from numpy import log10 
from plotly.graph_objs import Scatter
import pytest

from glue.app.qt import GlueApplication
from glue.config import settings
from glue.core import Data 
from glue.viewers.scatter.qt import ScatterViewer

from glue_plotly.common.common import DEFAULT_FONT, data_count, layers_to_export, base_rectilinear_axis
from glue_plotly.common.scatter2d import trace_data_for_layer 

class TestScatter2D:

    def setup_method(self, method):
        self.data1 = Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label='d1')
        self.data2 = Data(x=[1, 2, 3], y=[1, 4, 9], z=[1, 8, 27], label='d2')
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data1)
        self.app.session.data_collection.append(self.data2)
        for attr in ['x', 'y', 'z']:
            link = LinkSame(self.data1.id[attr], self.data2.id[attr])
            self.app.data_collection.add_link(link)
        self.viewer = self.app.new_data_viewer(ScatterViewer)
        self.viewer.add_data(self.data1)
        self.viewer.add_data(self.data2)
        for subtool in self.viewer.toolbar.tools['save'].subtools:
            if subtool.tool_id == 'save:plotly2d':
                self.tool = subtool
                break
        else:
            raise Exception("Could not find save:plotly2d tool in viewer")

    def teardown_method(self, method):
        self.viewer.close(warn=False)
        self.viewer = None
        self.app.close()
        self.app = None

    @pytest.mark.parametrize('log_x, log_y', product([True, False], repeat=2))
    def test_rectilinear_plot(self, log_x, log_y):

        # Set up viewer state
        viewer_state = self.viewer.state
        viewer_state.x_att = self.data1.id['x']
        viewer_state.y_att = self.data1.id['y']
        viewer_state.x_axislabel_size = 12
        viewer_state.y_axislabel_size = 8
        viewer_state.x_ticklabel_size = 6
        viewer_state.y_ticklabel_size = 12
        viewer_state.x_log = log_x
        viewer_state.y_log = log_y
        viewer_state.x_min = 1
        viewer_state.x_max = 10
        viewer_state.y_min = 0
        viewer_state.y_max = 8
        viewer_state.x_axislabel = 'X Axis'
        viewer_state.y_axislabel = 'Y Axis'

        # General viewer items
        export_layers = layers_to_export(self.viewer)
        assert len(export_layers) == 2
        assert data_count(export_layers) == 2

        # Axes
        x_axis = base_rectilinear_axis(self.viewer, 'x')
        y_axis = base_rectilinear_axis(self.viewer, 'y')

        common_items = dict(showgrid=False, showline=True, mirror=True, rangemode='normal',
                            zeroline=False, showspikes=False, showticklabels=True,
                            linecolor=settings.FOREGROUND_COLOR, tickcolor=settings.FOREGROUND_COLOR)
        assert common_items.items() <= x_axis.items()
        assert common_items.items() <= y_axis.items()

        assert x_axis['title'] == 'X Axis'
        assert y_axis['title'] == 'Y Axis'
        assert x_axis['type'] == 'log' if log_x else 'linear'
        assert y_axis['type'] == 'log' if log_y else 'linear'
        print(x_axis['range'])
        print(y_axis['range'])
        assert x_axis['range'] == [1, 10] if log_x else [0.0, 1.0]
        assert y_axis['range'] == [0, 8] if log_y else [0, log10(8)]

        base_font_dict = dict(family=DEFAULT_FONT, color=settings.FOREGROUND_COLOR)
        assert x_axis['titlefont'] == dict(**base_font_dict, size=24)
        assert y_axis['titlefont'] == dict(**base_font_dict, size=16)
        assert x_axis['tickfont'] == dict(**base_font_dict, size=9)
        assert y_axis['tickfont'] == dict(**base_font_dict, size=18)

        if log_x:
            assert x_axis['dtick'] == 1
            assert x_axis['minor_ticks'] == 'outside'
        if log_y:
            assert y_axis['dtick'] == 1
            assert y_axis['minor_ticks'] == 'outside'

        layer1 = self.viewer.layers[0]
        layer1.state.line_visible = True
        layer1.state.linewidth = 2
        layer1.state.linestyle = 'dashed'
        layer1.state.alpha = 0.64
        layer1.state.color = '#ff0000'
        layer1.state.xerr_visible = True
        layer1.state.yerr_visible = True
        layer1.state.xerr_att = self.data1.id['x']
        layer1.state.yerr_att = self.data1.id['y']

        traces1 = trace_data_for_layer(self.viewer, layer1, hover_data=None, add_data_label=True)
        assert set(traces1.keys()) == {'scatter', 'xerr', 'yerr'}
        scatter1 = traces1['scatter'][0]
        assert isinstance(scatter1, Scatter)
        assert scatter1['mode'] == 'lines+markers'
        assert scatter1['name'] == 'd1'
        assert scatter1['marker'].to_plotly_json() == dict(color='#ff0000', size=6, opacity=0.64,
                                                           line=dict(width=0))
        
        layer2 = self.viewer.layers[1]
        layer2.state.size = 3
        layer2.state.size_mode = 'Linear'
        layer2.state.cmap_mode = 'Linear'
        layer2.state.alpha = 0.9
        layer2.state.cmap = colormaps.get_cmap('magma')
        layer2.state.vector_visible = True
        layer2.state.vx_att = self.data2.id['y']
        layer2.state.vy_att = self.data2.id['z']
        layer2.state.fill = False
        layer2.state.vector_arrowhead = True
        layer2.state.vector_mode = 'Cartesian'
        layer2.state.vector_origin = 'middle'
        layer2.state.vector_scaling = 0.5

        hover_components = [self.data2.id['x'], self.data2.id['y']]
        hover_data = [cid in hover_components for cid in layer2.layer.components]
        traces2 = trace_data_for_layer(self.viewer, layer2, hover_data=hover_data, add_data_label=True)
        assert set(traces2.keys()) == {'scatter', 'vector'}
        scatter2 = traces2['scatter'][0]
        assert isinstance(scatter2, Scatter)
        assert scatter2['mode'] == 'markers'
        assert scatter2['name'] == 'd2'


