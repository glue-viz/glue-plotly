from itertools import product
from glue.core.link_helpers import LinkSame
from glue.core.visual import cmap

import numpy as np
from matplotlib import colormaps
from plotly.graph_objs import Scatter
import pytest

from glue.app.qt import GlueApplication
from glue.config import settings
from glue.core import Data 
from glue.viewers.scatter.qt import ScatterViewer

from glue_plotly.common.common import DEFAULT_FONT, data_count, layers_to_export, base_rectilinear_axis, sanitize
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


class TestScatter2DRectilinear(TestScatter2D):
    
    def setup_method(self, method):
        super().setup_method(method)

        viewer_state = self.viewer.state
        viewer_state.x_att = self.data1.id['x']
        viewer_state.y_att = self.data1.id['y']
        viewer_state.x_axislabel_size = 12
        viewer_state.y_axislabel_size = 8
        viewer_state.x_ticklabel_size = 6
        viewer_state.y_ticklabel_size = 12
        viewer_state.x_min = 1
        viewer_state.x_max = 10
        viewer_state.y_min = 0
        viewer_state.y_max = 8
        viewer_state.x_axislabel = 'X Axis'
        viewer_state.y_axislabel = 'Y Axis'

        # Set up first layer
        self.layer1 = self.viewer.layers[0]
        self.layer1.state.line_visible = True
        self.layer1.state.linewidth = 2
        self.layer1.state.linestyle = 'dashed'
        self.layer1.state.alpha = 0.64
        self.layer1.state.color = '#ff0000'
        self.layer1.state.xerr_visible = True
        self.layer1.state.yerr_visible = True
        self.layer1.state.xerr_att = self.data1.id['x']
        self.layer1.state.yerr_att = self.data1.id['y']

        # Set up second layer
        self.layer2 = self.viewer.layers[1]
        self.layer2.state.size = 3
        self.layer2.state.size_mode = 'Linear'
        self.layer2.state.cmap_mode = 'Linear'
        self.layer2.state.alpha = 0.9
        self.layer2.state.cmap = colormaps.get_cmap('magma')
        self.layer2.state.vector_visible = True
        self.layer2.state.vx_att = self.data2.id['y']
        self.layer2.state.vy_att = self.data2.id['z']
        self.layer2.state.fill = False
        self.layer2.state.vector_arrowhead = True
        self.layer2.state.vector_mode = 'Cartesian'
        self.layer2.state.vector_origin = 'middle'
        self.layer2.state.vector_scaling = 0.5

    def test_basic(self):
        export_layers = layers_to_export(self.viewer)
        assert len(export_layers) == 2
        assert data_count(export_layers) == 2

        x1 = self.data1['x']
        y1 = self.data1['y']
        mask1, (x1_san, y1_san) = sanitize(x1, y1)
        assert np.sum(mask1) == 3
        assert len(x1_san) == 3
        assert len(y1_san) == 3

        x2 = self.data2['x']
        y2 = self.data2['y']
        mask2, (x2_san, y2_san) = sanitize(x2, y2)
        assert np.sum(mask2) == 3
        assert len(x2_san) == 3
        assert len(y2_san) == 3

    @pytest.mark.parametrize('log_x, log_y', product([True, False], repeat=2))
    def test_axes(self, log_x, log_y):
        self.viewer.state.x_log = log_x
        self.viewer.state.y_log = log_y
        self.viewer.state.x_axislabel = 'X Axis'
        self.viewer.state.y_axislabel = 'Y Axis'

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
        assert x_axis['range'] == [1, 10] if log_x else [0.0, 1.0]
        assert y_axis['range'] == [0, 8] if log_y else [0, np.log10(8)]

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

    @pytest.mark.parametrize('cmap_mode', ['Fixed', 'Linear'])
    def test_error_bars(self, cmap_mode):
        self.viewer.state.cmap_mode = cmap_mode


    @pytest.mark.parametrize('log_x, log_y', product([True, False], repeat=2))
    def test_rectilinear_plot(self, log_x, log_y):

        traces1 = trace_data_for_layer(self.viewer, self.layer1, hover_data=None, add_data_label=True)
        print(traces1)
        assert set(traces1.keys()) == {'scatter'}
        scatter1 = traces1['scatter'][0]
        assert isinstance(scatter1, Scatter)
        assert scatter1['mode'] == 'lines+markers'
        assert scatter1['name'] == 'd1'
        assert scatter1['marker'].to_plotly_json() == dict(color='#ff0000', size=3, opacity=0.64,
                                                           line=dict(width=0))
        print(traces1['xerr']) 
        xerr = traces1['xerr']
        yerr = traces1['yerr']
        assert len(xerr) == 3
        assert len(yerr) == 3
        for arr in [xerr, yerr]:
            for err in arr:
                assert isinstance(err, Scatter)
                assert err['marker'] == dict(color="#ff0000")
                assert err['hoverinfo'] == 'skip'
                assert err['hovertext'] is None
                assert err['mode'] == 'markers'

        


        hover_components = [self.data2.id['x'], self.data2.id['y']]
        hover_data = [cid in hover_components for cid in self.layer2.layer.components]
        traces2 = trace_data_for_layer(self.viewer, self.layer2, hover_data=hover_data, add_data_label=True)
        assert set(traces2.keys()) == {'scatter', 'vector'}
        scatter2 = traces2['scatter'][0]
        assert isinstance(scatter2, Scatter)
        assert scatter2['mode'] == 'markers'
        assert scatter2['name'] == 'd2'


