from glue_jupyter.common.state_widgets.layer_scatter import ScatterLayerStateWidget
from traitlets import Bool


class PlotlyScatterLayerStateWidget(ScatterLayerStateWidget):

    template_file = (__file__, "layer_state_widget.vue")
    border_color_menu_open = Bool(default_value=False).tag(sync=True)
