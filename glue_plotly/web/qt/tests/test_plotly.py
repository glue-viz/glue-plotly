from __future__ import absolute_import, division, print_function
from glue_qt.app.application import get_icon

import pytest
import numpy as np

from glue.core import Data, DataCollection

pytest.importorskip('qtpy')

from glue_qt.app import GlueApplication  # noqa: E402
from glue_qt.viewers.scatter import ScatterViewer  # noqa: E402
from glue_qt.viewers.histogram import HistogramViewer  # noqa: E402
from glue_qt.viewers.profile import ProfileViewer  # noqa: E402

from ...export_plotly import build_plotly_call  # noqa: E402
from ....common.tests.utils import SimpleCoordinates  # noqa: E402

get_icon


class TestPlotly(object):

    def setup_method(self, method):
        d = Data(x=[1, 2, 3], y=[2, 3, 4], z=['a', 'b', 'c'], label='data')
        pd = Data(label='profile', w=np.arange(24).reshape((3, 4, 2)).astype(float))
        pd.coords = SimpleCoordinates()
        dc = DataCollection([d, pd])
        self.app = GlueApplication(dc)
        self.data = d
        self.profile_data = pd

    def teardown_method(self, method):
        self.app.close()
        self.app = None

    def test_scatter(self):

        d = self.data
        d.style.markersize = 6
        d.style.color = '#ff0000'
        d.style.alpha = .4

        viewer = self.app.new_data_viewer(ScatterViewer, data=d)
        viewer.state.x_att = d.id['y']
        viewer.state.y_att = d.id['x']

        args, kwargs = build_plotly_call(self.app)
        data = args[0]['data'][0].to_plotly_json()

        expected = dict(type='scatter', mode='markers', name=d.label,
                        marker=dict(size=6, opacity=0.4,
                                    color="#ff0000",
                                    line=dict(width=0)))
        for k, v in expected.items():
            assert data[k] == v

        np.testing.assert_array_equal(data['x'], d['y'])
        np.testing.assert_array_equal(data['y'], d['x'])

        layout = args[0]['layout']
        assert layout['showlegend']

        viewer.close(warn=False)

    def test_scatter_subset(self):

        d = self.data
        s = d.new_subset(label='subset')
        s.subset_state = d.id['x'] > 1
        s.style.marker = 's'

        viewer = self.app.new_data_viewer(ScatterViewer, data=d)
        viewer.state.x_att = d.id['x']
        viewer.state.y_att = d.id['x']

        args, kwargs = build_plotly_call(self.app)
        data = args[0]['data']

        # check that subset is on Top
        assert len(data) == 2
        assert data[0]['name'] == 'data'
        assert data[1]['name'] == 'subset'

        viewer.close(warn=False)

    def test_axes(self):

        viewer = self.app.new_data_viewer(ScatterViewer, data=self.data)

        viewer.state.x_log = True
        viewer.state.x_min = 10
        viewer.state.x_max = 100
        viewer.state.x_att = self.data.id['x']

        viewer.state.y_log = False
        viewer.state.y_min = 2
        viewer.state.y_max = 4
        viewer.state.y_att = self.data.id['y']

        args, kwargs = build_plotly_call(self.app)

        xaxis = dict(type='log', rangemode='normal',
                     range=[1, 2], title=viewer.state.x_axislabel, zeroline=False)
        yaxis = dict(type='linear', rangemode='normal',
                     range=[2, 4], title=viewer.state.y_axislabel, zeroline=False)
        layout = args[0]['layout']
        for k, v in layout['xaxis'].items():
            assert xaxis.get(k, v) == v
        for k, v in layout['yaxis'].items():
            assert yaxis.get(k, v) == v

        viewer.close(warn=False)

    def test_histogram(self):

        d = self.data
        d.style.color = '#000000'

        viewer = self.app.new_data_viewer(HistogramViewer, data=d)
        viewer.state.x_att = d.id['y']
        viewer.state.hist_x_min = 0
        viewer.state.hist_x_max = 10
        viewer.state.hist_n_bin = 20

        args, kwargs = build_plotly_call(self.app)

        expected = dict(
            name='data',
            type='bar',
            marker=dict(
                color='#000000',
                opacity=0.8,
                line=dict(width=0)
            ),
        )
        data = args[0]['data']
        trace_data = data[0].to_plotly_json()
        for k in expected:
            assert expected[k] == trace_data[k]

        layout = args[0]['layout']
        assert layout['barmode'] == 'overlay'
        assert layout['bargap'] == 0

        viewer.close(warn=False)

    def test_profile(self):

        d = self.profile_data
        d.style.color = '#000000'

        viewer = self.app.new_data_viewer(ProfileViewer, data=d)
        viewer.state.reference_data = d

        args, kwargs = build_plotly_call(self.app)

        expected = dict(
            name='profile',
            type='scatter',
            opacity=0.8,
            hoverinfo='skip',
            line=dict(
                width=2,
                shape='hvh',
                color='#000000'
            )
        )
        data = args[0]['data']
        trace_data = data[0].to_plotly_json()
        for k in expected:
            assert expected[k] == trace_data[k]

        layout = args[0]['layout']
        assert layout['barmode'] == 'overlay'
        assert layout['bargap'] == 0

        viewer.close(warn=False)

    def test_scatter_categorical(self):

        viewer = self.app.new_data_viewer(ScatterViewer, data=self.data)

        viewer.state.x_att = self.data.id['x']
        viewer.state.y_att = self.data.id['z']

        args, kwargs = build_plotly_call(self.app)

        xaxis = dict(type='linear', rangemode='normal',
                     range=[0.92, 3.08], title='x', zeroline=False)
        yaxis = dict(type='linear', rangemode='normal',
                     range=[-0.62, 2.62], title='z', zeroline=False)
        layout = args[0]['layout']
        for k, v in layout['xaxis'].items():
            assert xaxis.get(k, v) == v
        for k, v in layout['yaxis'].items():
            assert yaxis.get(k, v) == v

        viewer.close(warn=False)

    def test_histogram_categorical(self):

        viewer = self.app.new_data_viewer(HistogramViewer, data=self.data)

        viewer.state.x_att = self.data.id['z']

        args, kwargs = build_plotly_call(self.app)

        xaxis = dict(type='linear', rangemode='normal',
                     range=[-0.5, 2.5], title=viewer.state.x_axislabel, zeroline=False)
        yaxis = dict(type='linear', rangemode='normal',
                     range=[0, 1.2], title=viewer.state.y_axislabel, zeroline=False)
        layout = args[0]['layout']
        for k, v in layout['xaxis'].items():
            assert xaxis.get(k, v) == v
        for k, v in layout['yaxis'].items():
            assert yaxis.get(k, v) == v

        viewer.close(warn=False)
