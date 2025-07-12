from glue_jupyter.vuetify_helpers import link_glue_choices
from ipyvuetify.VuetifyTemplate import VuetifyTemplate
from traitlets import Bool, Int, List, observe

from glue_plotly.html_exporters.base_save_hover import BaseSaveHoverDialog


class JupyterSaveHoverDialog(BaseSaveHoverDialog, VuetifyTemplate):

    template_file = (__file__, "save_hover.vue")
    dialog_open = Bool().tag(sync=True)

    data_items = List().tag(sync=True)
    data_selected = Int().tag(sync=True)

    component_items = List().tag(sync=True)
    component_selected = List().tag(sync=True)

    def __init__(self,
                 data_collection,
                 checked_dictionary=None,
                 on_cancel=None,
                 on_export=None,
                 display=False):

        BaseSaveHoverDialog.__init__(self,
                                     data_collection=data_collection,
                                     checked_dictionary=checked_dictionary)
        VuetifyTemplate.__init__(self)

        self.on_cancel = on_cancel
        self.on_export = on_export

        if display:
            self.dialog_open = True

        link_glue_choices(self, self.state, "data")

        self._on_data_change()

    def _on_data_change(self, *args):
        super()._on_data_change(*args)
        data_components = self.state.data.components
        self.component_items = [
            {"text": component.label, "value": index}
            for index, component in enumerate(data_components)
        ]
        default_checked = { component.label: False for component in data_components }
        current_selections = self.checked_dictionary.get(self.state.data.label,
                                                         default_checked)
        self.component_selected = [i for i, component in enumerate(data_components)
                                   if current_selections[component.label]]

    @observe("component_selected")
    def _on_component_selected_changed(self, change):
        selections = change["new"]
        current_layer = self.state.data.label
        layer_checked_data = {
            component.label: i in selections
            for i, component in enumerate(self.state.data.components)
        }

        self.checked_dictionary[current_layer] = layer_checked_data
    def vue_select_none(self, *args):
        self.component_selected = []

    def vue_select_all(self, *args):
        self.component_selected = list(range(len(self.component_items)))

    def vue_cancel_dialog(self, *args):
        self.checked_dictionary = {}
        self.dialog_open = False
        if self.on_cancel is not None:
            self.on_cancel()

    def vue_export_viewer(self, *args):
        self.dialog_open = False
        if self.on_export is not None:
            self.on_export()
