from contextlib import nullcontext
from uuid import uuid4

from echo import delay_callback
from glue.core.command import ApplySubsetState

import plotly.graph_objects as go

from glue_plotly.common.common import base_layout_config

from glue_jupyter.view import IPyWidgetView


__all__ = ['PlotlyBaseView']

INTERACT_COLOR = "#cbcbcb"


class PlotlyBaseView(IPyWidgetView):

    LAYOUT_SETTINGS = dict(
        include_dimensions=False,
        hovermode=False, hoverdistance=1,
        dragmode=False, showlegend=False, grid=None,
        newselection=dict(line=dict(color=INTERACT_COLOR), mode='immediate'),
        modebar=dict(remove=['toimage', 'zoom', 'pan', 'lasso', 'zoomIn2d',
                             'zoomOut2d', 'select', 'autoscale', 'resetScale2d',
                             'resetViews'])
    )

    allow_duplicate_data = False
    allow_duplicate_subset = False
    is2d = True

    def __init__(self, session, state=None):

        super(PlotlyBaseView, self).__init__(session, state=state)

        layout = self._create_layout_config()
        self.figure = go.FigureWidget(layout=layout)

        self.selection_layer_id = uuid4().hex
        selection_layer = go.Heatmap(x0=0.5,
                                     dx=1,
                                     y0=0,
                                     dy=1,
                                     meta=self.selection_layer_id,
                                     z=[[[0, 0, 0, 0]]],
                                     visible=False)
        self.figure.add_trace(selection_layer)

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
    def selection_layer(self):
        return next(self.figure.select_traces(dict(meta=self.selection_layer_id)))

    def _create_layout_config(self):
        return base_layout_config(self, **self.LAYOUT_SETTINGS, width=1200, height=800)

    def _remove_trace_index(self, trace):
        # TODO: It feels like there has to be a better way to do this
        try:
            index = self.figure.data.index(trace)
            self.figure.data = self.figure.data[:index] + self.figure.data[index + 1:]
        except ValueError:
            pass

    def _remove_traces(self, traces):
        self.figure.data = [t for t in self.figure.data if t not in traces]

    def _clear_traces(self):
        self.figure.data = [self.selection_layer]

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

    def _update_selection_layer_bounds(self):
        x0 = 0.5 * (self.state.x_min + self.state.x_max)
        dx = self.state.x_max - self.state.x_min
        y0 = 0.5 * (self.state.y_min + self.state.y_max)
        dy = self.state.y_max - self.state.y_min
        self.selection_layer.update(x0=x0, dx=dx, y0=y0, dy=dy)

    def set_selection_active(self, visible):
        if visible:
            self._update_selection_layer_bounds()
        # self.selection_layer.update(visible=visible)

    def set_selection_callback(self, on_selection):
        self.selection_layer.on_selection(on_selection)

    def _update_plotly_x_limits(self, *args):
        with self.figure.batch_update():
            if self.state.x_min is not None and self.state.x_max is not None:
                self.axis_x['range'] = [self.state.x_min, self.state.x_max]

    def _update_plotly_y_limits(self, *args):
        with self.figure.batch_update():
            if self.state.y_min is not None and self.state.y_max is not None:
                self.axis_y['range'] = [self.state.y_min, self.state.y_max]

    def _update_axes_visible(self, *args):
        with self.figure.batch_update():
            self.axis_x.visible = self.state.show_axes
            self.axis_y.visible = self.state.show_axes

    def _set_x_state_bounds(self, x_range):
        with delay_callback(self.state, 'x_min', 'x_max'):
            self.state.x_min = x_range[0]
            self.state.x_max = x_range[1]

    def _set_y_state_bounds(self, y_range):
        with delay_callback(self.state, 'y_min', 'y_max'):
            self.state.y_min = y_range[0]
            self.state.y_max = y_range[1]

    @property
    def figure_widget(self):
        return self.figure

    def apply_roi(self, roi, use_current=False):
        with self._output_widget or nullcontext():
            if len(self.layers) > 0:
                subset_state = self._roi_to_subset_state(roi)
                cmd = ApplySubsetState(data_collection=self._data,
                                       subset_state=subset_state,
                                       override_mode=use_current)
                self._session.command_stack.do(cmd)

    # Interface stub for now
    # TODO: Should we have anything here?
    def redraw(self):
        pass
