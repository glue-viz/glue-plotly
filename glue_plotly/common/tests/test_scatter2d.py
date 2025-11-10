from itertools import product

import pytest
from glue_qt.app import GlueApplication
from glue_qt.viewers.scatter import ScatterViewer
from numpy import log10, rad2deg
from numpy.testing import assert_equal
from plotly.graph_objs import Scatter, Scattergeo

from glue.config import settings
from glue.core import Data
from glue_plotly.common import (
    DEFAULT_FONT,
    base_rectilinear_axis,
    color_info,
    data_count,
    layers_to_export,
    sanitize,
)
from glue_plotly.common.scatter2d import (
    angle_ticks_text,
    base_marker,
    geo_annotations,
    geo_layout_config,
    geo_ticks,
    projection_type,
    rectilinear_2d_vectors,
    rectilinear_error_bars,
    rectilinear_lines,
    scatter_mode,
    trace_data_for_layer,
)
from glue_plotly.utils import PLOTLY_MAJOR_VERSION


class TestScatter2D:

    def setup_method(self, method):
        self.data = Data(x=[1, 2, 3], y=[4, 5, 6], z=[7, 8, 9], label="d1")
        self.app = GlueApplication()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(ScatterViewer)
        self.viewer.add_data(self.data)

    def teardown_method(self, method):
        self.viewer.close(warn=False)
        self.viewer = None
        self.app.close()
        self.app = None


def test_angle_ticks_text_degrees():
    assert angle_ticks_text([-30, -10, 5, 11, 62], degrees=True) == \
            ["-30°", "-10°", "5°", "11°", "62°"]
    assert angle_ticks_text([0, 10, 20, 30, 40, 50], degrees=True) == \
            ["0°", "10°", "20°", "30°", "40°", "50°"]


def test_angle_ticks_text_radians():
    assert angle_ticks_text([-30, -15, 0, 45, 90], degrees=False) == \
            ["-π/6", "-π/12", "0", "π/4", "π/2"]
    assert angle_ticks_text([-67, 11, -24, 75, 180], degrees=False, digits=2) == \
            ["-1.17", "0.19", "-2π/15", "5π/12", "π"]
    assert angle_ticks_text([-67, 11, -24, 75, 180], degrees=False, digits=5) == \
            ["-1.16937", "0.19199", "-2π/15", "5π/12", "π"]


class TestScatter2DRectilinear(TestScatter2D):

    def setup_method(self, method):
        super().setup_method(method)

        viewer_state = self.viewer.state
        viewer_state.plot_mode = "rectilinear"
        viewer_state.x_att = self.data.id["x"]
        viewer_state.y_att = self.data.id["y"]
        viewer_state.x_axislabel_size = 12
        viewer_state.y_axislabel_size = 8
        viewer_state.x_ticklabel_size = 6
        viewer_state.y_ticklabel_size = 12
        viewer_state.x_min = 1
        viewer_state.x_max = 10
        viewer_state.y_min = 0
        viewer_state.y_max = 8
        viewer_state.x_axislabel = "X Axis"
        viewer_state.y_axislabel = "Y Axis"

        # Set up first layer
        self.layer = self.viewer.layers[0]
        self.layer.state.line_visible = True
        self.layer.state.alpha = 0.64
        self.layer.state.size_scaling = 1
        self.layer.state.size = 3
        self.layer.state.color = "#ff0000"
        self.layer.state.xerr_att = self.data.id["x"]
        self.layer.state.yerr_att = self.data.id["y"]

        self.mask, (self.x, self.y) = sanitize(self.data["x"], self.data["y"])

    def test_basic(self):
        export_layers = layers_to_export(self.viewer)
        assert len(export_layers) == 1
        assert data_count(export_layers) == 1

        assert sum(self.mask) == 3
        assert len(self.x) == 3
        assert len(self.y) == 3

    @pytest.mark.parametrize(("log_x", "log_y"), product([True, False], repeat=2))
    def test_axes(self, log_x, log_y):
        self.viewer.state.x_log = log_x
        self.viewer.state.y_log = log_y
        self.viewer.state.x_axislabel = "X Axis"
        self.viewer.state.y_axislabel = "Y Axis"

        x_axis = base_rectilinear_axis(self.viewer.state, "x")
        y_axis = base_rectilinear_axis(self.viewer.state, "y")

        common_items = dict(showgrid=False, showline=True, mirror=True,
                            rangemode="normal", zeroline=False,
                            showspikes=False, showticklabels=True,
                            linecolor=settings.FOREGROUND_COLOR,
                            tickcolor=settings.FOREGROUND_COLOR)
        assert common_items.items() <= x_axis.items()
        assert common_items.items() <= y_axis.items()

        if PLOTLY_MAJOR_VERSION == 6:
            assert x_axis["title"]["text"] == "X Axis"
            assert y_axis["title"]["text"] == "Y Axis"
        else:
            assert x_axis["title"] == "X Axis"
            assert y_axis["title"] == "Y Axis"

        assert x_axis["type"] == "log" if log_x else "linear"
        assert y_axis["type"] == "log" if log_y else "linear"

        x_lim_helper = self.viewer.state.x_lim_helper
        y_lim_helper = self.viewer.state.y_lim_helper
        expected_x_range = [x_lim_helper.lower, x_lim_helper.upper]
        expected_y_range = [y_lim_helper.lower, y_lim_helper.upper]
        if log_x:
            expected_x_range = list(log10(expected_x_range))
        if log_y:
            expected_y_range = list(log10(expected_y_range))
        assert x_axis["range"] == expected_x_range
        assert y_axis["range"] == expected_y_range

        base_font_dict = dict(family=DEFAULT_FONT, color=settings.FOREGROUND_COLOR)
        if PLOTLY_MAJOR_VERSION == 6:
            assert x_axis["title"]["font"] == dict(**base_font_dict, size=24)
            assert y_axis["title"]["font"] == dict(**base_font_dict, size=16)
        else:
            assert x_axis["titlefont"] == dict(**base_font_dict, size=24)
            assert y_axis["titlefont"] == dict(**base_font_dict, size=16)
        assert x_axis["tickfont"] == dict(**base_font_dict, size=9)
        assert y_axis["tickfont"] == dict(**base_font_dict, size=18)

        if log_x:
            assert x_axis["dtick"] == 1
            assert x_axis["minor_ticks"] == "outside"
        if log_y:
            assert y_axis["dtick"] == 1
            assert y_axis["minor_ticks"] == "outside"

    @pytest.mark.parametrize("fill", [True, False])
    def test_base_marker(self, fill):
        self.layer.state.fill = fill
        marker = base_marker(self.layer.state, self.mask)
        assert marker["size"] == 3
        assert marker["opacity"] == 0.64
        if fill:
            assert marker["line"] == dict(width=0)
            assert marker["color"] == "#ff0000"
        else:
            assert marker["color"] == "rgba(0,0,0,0)"
            assert marker["line"] == dict(width=1, color="#ff0000")

    def test_rectilinear_error_bars_cmap(self):
        layer_state = self.layer.state
        layer_state.cmap_mode = "Linear"
        layer_state.xerr_visible = True
        layer_state.yerr_visible = True
        marker = base_marker(layer_state, self.mask)
        xerr, xerr_traces = rectilinear_error_bars(layer_state, marker, self.mask,
                                                   self.x, self.y, "x")
        yerr, yerr_traces = rectilinear_error_bars(layer_state, marker, self.mask,
                                                   self.x, self.y, "y")

        mask_size = sum(self.mask)
        assert len(xerr["array"]) == mask_size
        assert len(yerr["array"]) == mask_size

        color = color_info(layer_state, self.mask)
        for traces in [xerr_traces, yerr_traces]:
            for i, bar in enumerate(traces):
                assert isinstance(bar, Scatter)
                assert bar["x"] == self.x[i]
                assert bar["y"] == self.y[i]
                assert bar["mode"] == "markers"
                assert bar["hoverinfo"] == "skip"
                assert bar["hovertext"] is None
                assert bar["marker"]["color"] == color[i]

    def test_rectilinear_error_bars_fixed_color(self):
        layer_state = self.layer.state
        layer_state.cmap_mode = "Fixed"
        layer_state.xerr_visible = True
        layer_state.yerr_visible = True
        marker = base_marker(layer_state, self.mask)
        xerr, xerr_traces = rectilinear_error_bars(layer_state, marker, self.mask,
                                                   self.x, self.y, "x")
        yerr, yerr_traces = rectilinear_error_bars(layer_state, marker, self.mask,
                                                   self.x, self.y, "y")

        mask_size = sum(self.mask)
        assert len(xerr["array"]) == mask_size
        assert len(yerr["array"]) == mask_size

        assert len(xerr_traces) == 0
        assert len(yerr_traces) == 0

    def test_rectilinear_lines_fixed_color(self):
        layer_state = self.layer.state
        layer_state.cmap_mode = "Fixed"
        layer_state.line_visible = True
        layer_state.linestyle = "dashed"
        layer_state.linewidth = 4
        marker = base_marker(layer_state, self.mask)
        mode = scatter_mode(layer_state)
        line, traces = rectilinear_lines(layer_state, marker, self.x, self.y)
        assert mode == "lines+markers"
        assert line["dash"] == "dash"
        assert line["width"] == 4
        assert len(traces) == 0

    def test_rectilinear_lines_cmap(self):
        layer_state = self.layer.state
        layer_state.cmap_mode = "Linear"
        layer_state.line_visible = True
        layer_state.linestyle = "dotted"
        layer_state.linewidth = 6
        marker = base_marker(layer_state, self.mask)
        mode = scatter_mode(layer_state)
        line, traces = rectilinear_lines(layer_state, marker, self.x, self.y)
        assert mode == "markers"
        assert line["dash"] == "dot"
        assert line["width"] == 6
        for trace in traces:
            assert isinstance(trace, Scatter)
            assert trace["mode"] == "lines"
            assert trace["showlegend"] is False
            assert trace["hoverinfo"] == "skip"
            assert trace["line"]["dash"] == "dot"
            assert trace["line"]["width"] == 6

    @pytest.mark.parametrize("cmap_mode", ["Fixed", "Linear"])
    def test_rectilinear_vectors(self, cmap_mode):
        layer_state = self.layer.state
        layer_state.vector_visible = True
        layer_state.vector_origin = "tail"
        layer_state.vector_arrowhead = True
        layer_state.cmap_mode = cmap_mode

        marker = base_marker(layer_state, self.mask)
        traces = rectilinear_2d_vectors(self.viewer, layer_state, marker,
                                        self.mask, self.x, self.y)
        color = color_info(layer_state, self.mask)
        if cmap_mode == "Fixed":
            assert len(traces) == 1
            trace = traces[0]
            assert trace["marker"]["color"] == color
        elif cmap_mode == "Linear":
            assert len(traces) == sum(self.mask)
            for i, trace in enumerate(traces):
                assert trace["line_color"] == color[i]

    def test_rectilinear_traces(self):
        self.layer.state.vector_visible = True
        self.layer.state.xerr_visible = True
        self.layer.state.yerr_visible = True

        hover_components = [self.data.id["x"], self.data.id["z"]]
        hover_data = { cid.label: cid in hover_components \
                       for cid in self.layer.layer.components }
        traces = trace_data_for_layer(self.viewer, self.layer.state,
                                      hover_data=hover_data,
                                      add_data_label=True)
        assert set(traces.keys()) == {"scatter", "vector"}
        scatter = traces["scatter"][0]
        assert scatter["hoverinfo"] == "text"
        assert len(scatter["hovertext"]) == len(self.layer.layer.main_components)


class TestScatter2DFullSphere(TestScatter2D):

    MODES = ("aitoff", "hammer", "lambert", "mollweide")

    def setup_method(self, method):
        super().setup_method(method)

        self.viewer.state.x_axislabel_size = 3
        self.viewer.state.y_axislabel_size = 12

        self.layer = self.viewer.layers[0]
        self.layer.state.color = "#ff0000"
        self.layer.state.size = 5
        self.layer.state.size_scaling = 1
        self.layer.state.alpha = 0.5

    def test_basic(self):
        export_layers = layers_to_export(self.viewer)
        assert len(export_layers) == 1
        assert data_count(export_layers) == 1

        assert len(self.data["x"]) == 3
        assert len(self.data["y"]) == 3

    @pytest.mark.parametrize("mode", MODES)
    def test_layout(self, mode):
        self.viewer.state.plot_mode = mode
        layout = geo_layout_config(self.viewer)
        assert layout["dragmode"] is False

        geo = layout["geo"]
        assert geo["projection_type"] == projection_type(self.viewer.state)

        for show in ("showcoastlines", "showcountries", "showlakes",
                     "showland", "showocean", "showrivers"):
            assert geo[show] is False

        assert geo["scope"] == "world"
        assert geo["domain"]["x"] == [0.05, 0.95]
        assert geo["domain"]["y"] == [0.05, 0.95]

    @pytest.mark.parametrize(("mode", "angle_unit"),
                             product(MODES, ("radians", "degrees")))
    def test_ticks(self, mode, angle_unit):
        self.viewer.state.plot_mode = mode
        self.viewer.state.angle_unit = angle_unit
        ticks = geo_ticks(self.viewer.state)

        assert len(ticks) == 2

        for tick in ticks:
            assert isinstance(tick, Scattergeo)
            assert tick["showlegend"] is False
            assert tick["mode"] == "text"
            assert tick["hoverinfo"] == "skip"

        equator_ticks, edge_ticks = ticks

        degrees = angle_unit == "degrees"

        lon_angles = tuple(range(-150, 180, 30))
        assert equator_ticks["lon"] == lon_angles
        assert all(lat == 0 for lat in equator_ticks["lat"])
        assert equator_ticks["text"] == tuple(angle_ticks_text(lon_angles,
                                                               degrees=degrees))

        lat_angles = tuple(range(-75, 90, 15))
        assert edge_ticks["lat"] == lat_angles
        assert all(lon == -180 for lon in edge_ticks["lon"])
        assert edge_ticks["text"] == tuple(angle_ticks_text(lat_angles,
                                                            degrees=degrees))
        assert edge_ticks["textposition"] == \
            ("middle left",) * 4 + ("middle right",) * 3 + ("middle left",) * 4


    @pytest.mark.parametrize("mode", MODES)
    def test_annotations(self, mode):
        self.viewer.state.plot_mode = mode
        self.viewer.state.x_axislabel = "ABCDE"

        annotations = geo_annotations(self.viewer.state)
        assert len(annotations) == 2

        xlabel, ylabel = annotations
        assert xlabel["x"] == 0.5
        assert xlabel["y"] == 0
        assert xlabel["text"] == "ABCDE"
        assert xlabel["showarrow"] is False
        xfont = xlabel["font"]
        assert xfont["family"] == DEFAULT_FONT
        assert xfont["size"] == 4.5

        assert ylabel["x"] == (0.2 if mode == "lambert" else 0)
        assert ylabel["y"] == 0.5
        assert ylabel["text"] == "y"
        assert ylabel["showarrow"] is False
        yfont = ylabel["font"]
        assert yfont["family"] == DEFAULT_FONT
        assert yfont["size"] == 18

    @pytest.mark.parametrize(("mode", "angle_unit"),
                             product(MODES, ("radians", "degrees")))
    def test_traces(self, mode, angle_unit):
        self.viewer.state.plot_mode = mode
        self.viewer.state.angle_unit = angle_unit

        hover_components = [self.data.id["x"], self.data.id["z"]]
        hover_data = { cid.label: cid in hover_components \
                       for cid in self.layer.layer.components }
        traces = trace_data_for_layer(self.viewer, self.layer.state,
                                      hover_data=hover_data,
                                      add_data_label=True)

        assert set(traces.keys()) == {"scatter"}
        assert len(traces["scatter"]) == 1

        scatter = traces["scatter"][0]
        assert isinstance(scatter, Scattergeo)
        assert scatter["hoverinfo"] == "text"
        assert len(scatter["hovertext"]) == len(self.layer.layer.main_components)

        if angle_unit == "degrees":
            assert_equal(scatter["lon"], self.data["x"])
            assert_equal(scatter["lat"], self.data["y"])
        else:
            assert_equal(scatter["lon"], rad2deg(self.data["x"]))
            assert_equal(scatter["lat"], rad2deg(self.data["y"]))
