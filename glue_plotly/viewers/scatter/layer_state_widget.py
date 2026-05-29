from glue_jupyter.common.state_widgets.layer_scatter import ScatterLayerStateWidget
from traitlets import Bool


class PlotlyScatterLayerStateWidget(ScatterLayerStateWidget):

    template_file = (__file__, "layer_state_widget.vue")
