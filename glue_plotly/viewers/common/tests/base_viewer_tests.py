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
