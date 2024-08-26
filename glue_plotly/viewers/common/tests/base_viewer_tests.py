from uuid import UUID


class BasePlotlyViewTests:

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_unique_class(self):
        unique_class = self.viewer.unique_class
        prefix = "glue-plotly-"
        prefix_len = len(prefix)
        assert unique_class.startswith(prefix)
        assert len(unique_class) == prefix_len + 32

        # Test UUID validity by seeing if we can construct a UUID instance
        assert UUID(unique_class[prefix_len:])

        assert unique_class in self.viewer.figure._dom_classes

    def test_config(self):
        config = self.viewer.figure._config
        assert config["displayModeBar"] is False

    def test_log_x_axis(self):
        assert self.viewer.axis_x.type == "linear"
        self.viewer.state.x_log = True
        assert self.viewer.axis_x.type == "log"
        self.viewer.state.x_log = False
        assert self.viewer.axis_x.type == "linear"

    def test_log_y_axis(self):
        assert self.viewer.axis_y.type == "linear"
        self.viewer.state.y_log = True
        assert self.viewer.axis_y.type == "log"
        self.viewer.state.y_log = False
        assert self.viewer.axis_y.type == "linear"

    def test_set_x_axis_bounds(self):
        self.viewer.state.x_min = 1
        self.viewer.state.x_max = 25
        assert self.viewer.axis_x['range'] == (1, 25)
        self.viewer.state.x_log = True
        self.viewer.state.x_min = 10
        self.viewer.state.x_max = 1000
        assert self.viewer.axis_x['range'] == (1.0, 3.0)

    def test_set_y_axis_bounds(self):
        self.viewer.state.y_min = 1
        self.viewer.state.y_max = 25
        assert self.viewer.axis_y['range'] == (1, 25)
        self.viewer.state.y_log = True
        self.viewer.state.y_min = 10
        self.viewer.state.y_max = 1000
        assert self.viewer.axis_y['range'] == (1.0, 3.0)
