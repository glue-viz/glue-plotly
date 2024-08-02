from __future__ import absolute_import, division, print_function

import json
from importlib.metadata import version
from packaging.version import Version

import mock
import pytest
from mock import patch
from numpy import __version__ as numpy_version
from chart_studio.plotly import plotly
from plotly.exceptions import PlotlyError

from glue.core import Data, DataCollection
from glue_qt.app import GlueApplication
from glue_qt.viewers.histogram import HistogramViewer
from glue_qt.viewers.profile import ProfileViewer
from glue_qt.viewers.scatter import ScatterViewer
try:
    from glue_qt.plugins.dendro_viewer import DendrogramViewer
except ImportError:
    DendrogramViewer = None

from glue_plotly.web.export_plotly import build_plotly_call

from ..exporter import QtPlotlyExporter
from ....web.qt import setup

plotly_sign_in = mock.MagicMock()
plotly_plot = mock.MagicMock()


# glue-qt doesn't have a __version__ so we need to do this
GLUE_QT_GE_031 = Version(version("glue_qt")) > Version('0.3.1')
NUMPY_LT_2 = Version(numpy_version) < Version('2')


SIGN_IN_ERROR = """
Aw, snap! You tried to use our API as the user 'BATMAN', but
the supplied API key doesn't match our records. You can view
your API key at plot.ly/settings.
"""

MAX_PRIVATE_ERROR = """
This file cannot be saved as private, your current Plotly account has
filled its quota of private files. You can still save public files, or you can
upgrade your account to save more files privately by visiting your account at
https://plot.ly/settings/subscription. To make a file public in the API, set
the optional argument 'world_readable' to true.
"""


def make_credentials_file(path, username='', api_key=''):
    credentials = {}
    credentials['username'] = username
    credentials['api_key'] = api_key
    credentials['proxy_username'] = ''
    credentials['proxy_password'] = ''
    credentials['stream_ids'] = []
    with open(path, 'w') as f:
        json.dump(credentials, f, sort_keys=True)
    plotly.files.FILE_CONTENT[path] = credentials


class TestQtPlotlyExporter:

    def setup_class(self):

        setup()

        data = Data(x=[1, 2, 3], y=[2, 3, 4], label='data')
        dc = DataCollection([data])
        self.app = GlueApplication(dc)

        data.style.color = '#000000'
        hv = self.app.new_data_viewer(HistogramViewer, data=data)
        hv.component = data.id['y']
        hv.xmin = 0
        hv.xmax = 10
        hv.bins = 20

        sv = self.app.new_data_viewer(ScatterViewer, data=data)
        sv.state.x_att = data.id['x']
        sv.state.y_att = data.id['y']

        pv = self.app.new_data_viewer(ProfileViewer, data=data)
        pv.state.x_att = data.id['Pixel Axis 0 [x]']

        # Workaround until for the issue solved in https://github.com/glue-viz/glue-qt/pull/19
        if (NUMPY_LT_2 or GLUE_QT_GE_031) and DendrogramViewer is not None:
            dendro_data = Data(label='dendrogram', parent=[-1, 0, 1, 1], height=[1.3, 2.2, 3.2, 4.4])
            dc.append(dendro_data)
            dv = self.app.new_data_viewer(DendrogramViewer, data=dendro_data)
            dv.state.height_att = dendro_data.id['height']
            dv.state.parent_att = dendro_data.id['parent']

        self.args, self.kwargs = build_plotly_call(self.app)

    def teardown_class(self):
        self.app.close()
        self.app = None

    def get_exporter(self):
        return QtPlotlyExporter(plotly_args=self.args, plotly_kwargs=self.kwargs)

    def test_default_no_credentials(self, tmpdir):

        credentials_file = tmpdir.join('.credentials').strpath

        make_credentials_file(credentials_file)

        with patch('chart_studio.plotly.plotly.tools.CREDENTIALS_FILE', credentials_file):

            exporter = self.get_exporter()

            assert not exporter.radio_account_config.isChecked()
            assert exporter.radio_account_manual.isChecked()

            assert exporter.radio_sharing_secret.isChecked()

    def test_default_with_credentials(self, tmpdir):

        credentials_file = tmpdir.join('.credentials').strpath

        make_credentials_file(credentials_file, username='batman', api_key='batmobile')

        with patch('chart_studio.plotly.plotly.tools.CREDENTIALS_FILE', credentials_file):

            exporter = self.get_exporter()

            assert exporter.radio_account_config.isChecked()
            assert 'username: batman' in exporter.radio_account_config.text()
            assert exporter.radio_sharing_secret.isChecked()

    def test_edit_username_toggle_custom(self, tmpdir):

        credentials_file = tmpdir.join('.credentials').strpath

        make_credentials_file(credentials_file, username='batman', api_key='batmobile')

        with patch('chart_studio.plotly.plotly.tools.CREDENTIALS_FILE', credentials_file):

            exporter = self.get_exporter()

            assert exporter.radio_account_config.isChecked()
            exporter.username = 'a'
            assert exporter.radio_account_manual.isChecked()

            exporter.radio_account_config.setChecked(True)
            assert exporter.radio_account_config.isChecked()
            exporter.api_key = 'a'
            assert exporter.radio_account_manual.isChecked()

    def test_accept_default(self, tmpdir):

        credentials_file = tmpdir.join('.credentials').strpath

        make_credentials_file(credentials_file, username='batman', api_key='batmobile')

        with patch('chart_studio.plotly.plotly.tools.CREDENTIALS_FILE', credentials_file):
            with patch('chart_studio.plotly.plot', mock.MagicMock()):
                with patch('chart_studio.plotly.sign_in', mock.MagicMock()):
                    with patch('webbrowser.open_new_tab'):
                        exporter = self.get_exporter()
                        exporter.accept()
                        assert exporter.text_status.text() == 'Exporting succeeded'

    ERRORS = [
        (PlotlyError(SIGN_IN_ERROR), 'Authentication failed'),
        (PlotlyError(MAX_PRIVATE_ERROR), 'Maximum number of private plots reached'),
        (PlotlyError('Oh noes!'), 'An unexpected error occurred'),
        (TypeError('A banana is not an apple'), 'An unexpected error occurred')
    ]

    @pytest.mark.parametrize(('error', 'status'), ERRORS)
    def test_accept_errors(self, tmpdir, error, status):

        credentials_file = tmpdir.join('.credentials').strpath

        make_credentials_file(credentials_file, username='batman', api_key='batmobile')

        plot = mock.MagicMock(side_effect=error)

        sign_in = mock.MagicMock()

        with patch('chart_studio.plotly.plotly.tools.CREDENTIALS_FILE', credentials_file):
            with patch('chart_studio.plotly.sign_in', sign_in):
                with patch('chart_studio.plotly.plot', plot):
                    with patch('webbrowser.open_new_tab'):
                        exporter = self.get_exporter()
                        exporter.accept()
                        assert exporter.text_status.text() == status

    def test_fix_url(self, tmpdir):

        credentials_file = tmpdir.join('.credentials').strpath

        make_credentials_file(credentials_file, username='batman', api_key='batmobile')

        plot = mock.MagicMock(return_value='https://chart-studio.plotly.com/'
                                           '~batman/6/?share_key=rbkWvJQn6cyj3HMMGROiqI#/')

        sign_in = mock.MagicMock()

        with patch('chart_studio.plotly.plotly.tools.CREDENTIALS_FILE', credentials_file):
            with patch('chart_studio.plotly.sign_in', sign_in):
                with patch('chart_studio.plotly.plot', plot):
                    with patch('webbrowser.open_new_tab') as open_new_tab:
                        exporter = self.get_exporter()
                        exporter.accept()
                        open_new_tab.assert_called_once_with(
                            'https://chart-studio.plotly.com/~batman/6/?share_key=rbkWvJQn6cyj3HMMGROiqI#/')
