from echo import delay_callback
from glue.config import settings
from glue_jupyter.link import link
from glue_jupyter.view import IPyWidgetView

import plotly.graph_objects as go


INTERACT_COLOR = "#cbcbcb"


class PlotlyBaseView(IPyWidgetView):

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = True

    def __init__(self, session, state=None):

        super(PlotlyBaseView, self).__init__(session, state=state)

        x_axis = go.layout.XAxis(showgrid=False)
        y_axis = go.layout.YAxis(showgrid=False)
        self.plotly_layout = go.Layout(margin=dict(r=50, l=50, b=50, t=50),
                                       width=1200,
                                       height=600,
                                       grid=None,
                                       paper_bgcolor=settings.BACKGROUND_COLOR,
                                       plot_bgcolor=settings.BACKGROUND_COLOR,
                                       xaxis=x_axis,
                                       yaxis=y_axis,
                                       dragmode=False,
                                       newselection=dict(line=dict(color=INTERACT_COLOR), mode='immediate'),
                                       modebar=dict(remove=['toimage', 'zoom', 'pan', 'lasso', 'zoomIn2d', 'zoomOut2d', 'select']))
        self.figure = go.FigureWidget(layout=self.plotly_layout)
        self.figure.for_each_selection

        self.state.add_callback('x_axislabel', self.update_x_axislabel)
        self.state.add_callback('y_axislabel', self.update_y_axislabel)
        self.state.add_callback('x_min', self._update_plotly_x_limits)
        self.state.add_callback('x_max', self._update_plotly_x_limits)
        self.state.add_callback('y_min', self._update_plotly_y_limits)
        self.state.add_callback('y_max', self._update_plotly_y_limits)
        self.state.add_callback('show_axes', self._update_axes_visible)

        self.axis_x.on_change(lambda _obj, x_range: self._set_x_state_bounds(x_range), 'range')
        self.axis_y.on_change(lambda _obj, y_range: self._set_y_state_bounds(y_range), 'range')

        self._update_plotly_x_limits()
        self._update_plotly_y_limits()
        self._update_axes_visible()

        self.create_layout()

    @property
    def axis_x(self):
        return self.figure.layout.xaxis

    @property
    def axis_y(self):
        return self.figure.layout.yaxis

    def update_x_axislabel(self, label):
        self.axis_x['title'] = label

    def update_y_axislabel(self, label):
        self.axis_y['title'] = label

    def _update_plotly_x_limits(self, *args):
        print("_update_plotly_x_limits")
        print(self.axis_x['range'])
        with self.figure.batch_update():
            if self.state.x_min is not None and self.state.x_max is not None:
                self.axis_x['range'] = [self.state.x_min, self.state.x_max]

    def _update_plotly_y_limits(self, *args):
        print("_update_plotly_y_limits")
        print(self.axis_y['range'])
        with self.figure.batch_update():
            if self.state.y_min is not None and self.state.y_max is not None:
                self.axis_y['range'] = [self.state.y_min, self.state.y_max]

    def _update_axes_visible(self, *args):
        with self.figure.batch_update():
            self.axis_x.visible = self.state.show_axes
            self.axis_y.visible = self.state.show_axes

    def _set_x_state_bounds(self, x_range):
        print("_set_x_state_bounds", x_range)
        with delay_callback(self.state, 'x_min', 'x_max'):
            self.state.x_min = x_range[0]
            self.state.x_max = x_range[1]


    def _set_y_state_bounds(self, y_range):
        print("_set_y_state_bounds", y_range)
        with delay_callback(self.state, 'y_min', 'y_max'):
            self.state.y_min = y_range[0]
            self.state.y_max = y_range[1]

    @property
    def figure_widget(self):
        return self.figure

