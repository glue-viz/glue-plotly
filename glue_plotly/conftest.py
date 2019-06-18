def pytest_configure(config):
    from glue_plotly import setup
    setup()
